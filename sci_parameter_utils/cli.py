import click
import json
import sci_parameter_utils.nondim
import sci_parameter_utils.searcher
import sci_parameter_utils.template
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
        eset = sci_parameter_utils.template.TemplateElemSet(
            get_dict_from_file(params))
    except RuntimeError as e:
        click.echo("Error setting up template: {}".format(e))
        raise click.Abort()
    iReq = eset.get_inputs()
    if ifile:
        iList = get_dict_from_file(ifile)
        if not iList:
            iList = [{}]
    else:
        iList = [{}]

    templater = False
    extn = get_extn_from_file(template)
    templater = sci_parameter_utils.templater.get_templater_from_extn(extn)()
    if not out:
        out = templater.get_fn_suggest(template)
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
                ivals[k] = eset.validate(k, click.prompt(p))
            else:
                click.echo("No value supplied for {}".format(k))
                raise click.Abort()

        try:
            eset.compute_strs(ivals)

            fn = templater.replace(out, ivals)
            click.echo(fn)
            templater.template_file(template,
                                    click.open_file(fn, 'w'),
                                    ivals)
        except RuntimeError as e:
            click.echo("{}".format(e))
            raise click.Abort()


@cli_main.command('print')
@click.option('--defs', '-d', type=click.File('r'),
              required=True,
              help="Parmeter definition file")
@click.option('--locs', '-l', type=click.File('r'),
              required=True,
              help="Parameter location files")
@click.option('--print-consts/--no-print-consts', default=True,
              help="Indicate whether to include constants in output")
@click.option('--print-nondims/--no-print-nondims', default=True,
              help="Indicate whether to include nondimensional "
              "parameters in output")
@click.option('--print-scales/--no-print-scales', default=True,
              help="Indicate whether to include characteristic scales "
              "in output")
@click.argument('prmfiles', type=click.File('r'), nargs=-1)
def parse_nondim_params(prmfiles, defs, locs,
                        print_consts, print_nondims, print_scales):
    """Prints constants and derived nondimensional quantities
    defined in PRMFILES"""
    ndim = sci_parameter_utils.nondim.NonDim()
    ndim.add_from_dict(get_dict_from_file(defs))

    # Find searcher using first filename as hint
    searcher = False
    extn = get_extn_from_file(prmfiles[0])
    searcher = sci_parameter_utils.searcher.get_searcher_from_extn(extn)()
    searcher.add_from_dict(get_dict_from_file(locs))

    for f in prmfiles:
        click.echo("Input {}:".format(f.name))
        subs_list = searcher.parse_file(f)
        if print_consts:
            click.echo('Constants:')
            ndim.write_consts(click.get_text_stream('stdout'), subs_list)
        if print_nondims:
            click.echo('Nondimensional Parameters:')
            ndim.write_nondim(click.get_text_stream('stdout'), subs_list)
        if print_scales:
            click.echo('Scales:')
            ndim.write_scales(click.get_text_stream('stdout'), subs_list)
        click.echo('-----')


if(__name__ == "__main__"):
    cli_main()
