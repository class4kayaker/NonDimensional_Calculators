import click
import json
import sci_parameter_utils.nondim
import sci_parameter_utils.searcher
import yaml


def get_dict_from_file(fobj):
    """
    Get dictionary from a file by extn
    """
    if fobj.name.endswith('.yaml'):
        return yaml.safe_load(fobj)
    return json.load(fobj)


@click.command()
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
    fn1 = prmfiles[0].name
    hInd = fn1.rfind('.', -4)
    extn = ""
    if(hInd > 0):
        extn = fn1[hInd+1:]
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
    parse_nondim_params()
