import click
import json
import sci_parameter_utils.fragment
import sci_parameter_utils.parsers
import sci_parameter_utils.general
import yaml
try:
    import typing  # noqa: F401
    from typing import Any, Callable, Iterable, Type  # noqa: F401
except:
    pass


def get_dict_from_file(fobj):
    """
    Get dictionary from a file by extn
    """
    if fobj.name.endswith('.yaml'):
        return yaml.safe_load(fobj)
    return json.load(fobj)


def get_extn_from_file(fobj):
    fn = fobj.name
    hInd = fn.rfind('.', -4)
    if(hInd > 0):
        return fn[hInd+1:]
    return ""


def get_values_interactively(vlist, validator):
    # type: (Iterable[str], Callable[[str, str], Any]) -> Dict[str, Any]
    ivals = {}
    for k in vlist:
        def validate(v):
            return validator(k, v)
        ivals[k] = click.prompt("{}".format(k),
                                value_proc=validate)
    return ivals


@click.group()
def cli_main():
    """Set of useful parameter utilities"""


@cli_main.command()
@click.option('--params', '-p', type=click.File('r'),
              required=True,
              help="Parmeter definition file")
@click.option('--ifile', '-i', type=click.File('r'),
              help="Input values file")
@click.option('--out', '-o', default="",
              help="Name format for output file")
@click.option('--interact/--no-interact', default=False,
              help="Allow interactive value supply")
@click.option('list_fns', '--list/--no-list', '-l', default=False,
              help="List names of output files only")
@click.argument('template', type=click.File('r'))
def template(params, ifile, out, template, interact, list_fns):
    # type: (Any, Any, Any, Any, bool, bool) -> None
    # type: (typing.io.IO, typing.io.IO, typing.io.IO, typing.io.IO, bool, bool) -> None # noqa
    """Generate parameter files from TEMPLATE"""
    try:
        eset = sci_parameter_utils.fragment.TemplateElemSet(
            sci_parameter_utils.fragment.elems_from_dict(
                get_dict_from_file(params),
                sci_parameter_utils.fragment.TemplateElem
            ))
    except Exception as e:
        click.echo("Error setting up template: {}".format(e))
        raise click.Abort()

    iReq = eset.get_inputs()
    if ifile:
        iList = get_dict_from_file(ifile)
        if not iList:
            iList = [{}]
    else:
        iList = [{}]

    extn = get_extn_from_file(template)
    try:
        parser = (sci_parameter_utils.parsers.PFileParser
                  .parser_by_extn(extn))
    except Exception as e:
        click.echo("Error getting parser: {}".format(e))
        raise click.Abort()

    if not out:
        out = sci_parameter_utils.general.get_fn_suggest(template, parser)
    if not out:
        out = 'output.'+extn

    for d in iList:
        ivals = {}
        try:
            missing = iReq.difference(d.keys())

            for k in iReq:
                if k in d:
                    ivals[k] = eset.validate(k, d[k])
            if interact:
                click.echo('Getting input values')
                ivals.update(get_values_interactively(missing, eset.validate))

            missing = iReq.difference(ivals)
            if missing:
                raise ValueError("No values supplied for {}".format(missing))

        except Exception as e:
            click.echo("Error obtaining input values: {}".format(e))
            raise click.Abort()

        eset.compute_strings(ivals)
        fn = out.format(**ivals)
        try:
            pass

        except Exception as e:
            click.echo("Error generating filename: {}".format(e))
            raise click.Abort()

        if list_fns:
            click.echo(fn)
            continue

        try:
            (sci_parameter_utils.general
             .do_template(template,
                          click.open_file(fn, 'w'),
                          parser,
                          ivals))
        except Exception as e:
            click.echo("Error templating file {}: {}".format(fn, e))
            raise click.Abort()


@cli_main.command('print')
@click.option('--deffile', '-d', type=click.File('r'),
              required=True,
              help="Parmeter definition file")
@click.option('olist', '--print', '-p', default="",
              help="List of sections to print")
@click.argument('prmfiles', type=click.File('r'), nargs=-1)
def print_vals(prmfiles, deffile, olist):
    # type: (Any, Any, str) -> None
    """Prints values from PRMFILES"""
    try:
        idict = get_dict_from_file(deffile)
        deffile.close()
    except Exception as e:
        click.echo("Error setting loading def file: {}".format(e))
        raise click.Abort()

    try:
        dset = sci_parameter_utils.fragment.TemplateElemSet(
            sci_parameter_utils.fragment.elems_from_dict(
                idict['elems'],
                sci_parameter_utils.fragment.TemplateElem
            ))
    except Exception as e:
        click.echo("Error setting up template: {}".format(e))
        raise click.Abort()

    try:
        sset = sci_parameter_utils.fragment.elems_from_dict(
            idict['locs'],
            sci_parameter_utils.fragment.SearchElem
        )
    except Exception as e:
        click.echo("Error generating search list: {}".format(e))
        raise click.Abort()

    try:
        prlist = idict['print']

        if olist:
            pr_sections = set(s.strip() for s in olist.split(','))
        else:
            pr_sections = set(prlist.keys())
    except Exception as e:
        click.echo("Error collecting printing sections: {}".format(e))
        raise click.Abort()

    extn = get_extn_from_file(prmfiles[0])
    try:
        parser = (sci_parameter_utils.parsers.PFileParser
                  .parser_by_extn(extn))
    except Exception as e:
        click.echo("Error getting parser: {}".format(e))
        raise click.Abort()

    for f in prmfiles:
        click.echo("Input {}:".format(f.name))

        try:
            ivals = sci_parameter_utils.general.do_search(sset, f, parser)
        except Exception as e:
            click.echo("Error searching file: {}".format(e))
            raise click.Abort()

        try:
            dset.compute_strings(ivals)
        except Exception as e:
            click.echo("Error generating strings: {}".format(e))
            raise click.Abort()

        try:
            for k in prlist:
                if k in pr_sections:
                    click.echo('Section {}'.format(k))
                    for v in prlist[k]:
                        click.echo('\t{} = {}'.format(v, ivals[v]))
        except Exception as e:
            click.echo("Error printing data: {}".format(e))
            raise click.Abort()
        click.echo('-----')
