import click
import json
import sci_parameter_utils.nondim
import sci_parameter_utils.searcher
import sci_parameter_utils.fragment
import sci_parameter_utils.parsers
import sci_parameter_utils.templater
import yaml


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
@click.argument('template', type=click.File('r'))
def template(params, ifile, out, interact, template):
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
        out = sci_parameter_utils.templater.get_fn_suggest(template, parser)
    if not out:
        out = 'output.'+extn

    for d in iList:
        ivals = {}
        click.echo('Getting input values')
        for k in iReq:
            if k in d:
                ivals[k] = eset.validate(k, d[k])
            elif interact:
                p = "{}".format(k)
                while True:
                    try:
                        ivals[k] = eset.validate(k, click.prompt(p))
                    except ValueError as e:
                        click.echo('Bad value for {}: {}'.format(k, e))
            else:
                click.echo("No value supplied for {}".format(k))
                raise click.Abort()

        try:
            eset.compute_strings(ivals)

            fn = out.format(**ivals)
        except Exception as e:
            click.echo("Error generating filename: {}".format(fn, e))
            raise click.Abort()

        try:
            click.echo(fn)
            (sci_parameter_utils.templater
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
            olist = set(s.strip() for s in olist.split(','))
        else:
            olist = set(prlist.keys())
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
            ivals = sci_parameter_utils.searcher.do_search(sset, f, parser)
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
                if k in olist:
                    click.echo('Section {}'.format(k))
                    for v in prlist[k]:
                        click.echo('\t{} = {}'.format(v, ivals[v]))
        except Exception as e:
            click.echo("Error printing data: {}".format(e))
            raise click.Abort()
        click.echo('-----')


if(__name__ == "__main__"):
    cli_main()
