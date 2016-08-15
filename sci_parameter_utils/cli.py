import click
import sympy
import json
import sci_parameter_utils.nondim
import sci_parameter_utils.searcher
import yaml


def get_dict_from_file(fobj):
    if fobj.name.endswith('.yaml'):
        return yaml.safe_load(fobj)
    return json.load(fobj)


def print_constants(subs, ndim, verb=False):
    click.echo('Constants:')
    for v, n in subs.items():
        tex_var = sympy.latex(v)
        defn = ndim.get_const_desc(v)
        line = "   {:15}= {:13g}".format(tex_var, n)
        if verb and defn:
            line += ": {}".format(defn)
        click.echo(line)


def print_ndims(ndims, verb=False):
    click.echo('Nondimensional Parameters:')
    for c, val, expr in ndims:
        line = "   {:5}".format(c)
        if isinstance(val, sympy.Float):
            line += "={:10.2g}".format(float(val))
        else:
            line += "={}".format(val)
        if verb:
            line += "={}".format(expr)
        click.echo(line)


def list_scales(scales, verb=False):
    click.echo('Scales:')
    for c, val, expr in scales:
        line = "   {:5}".format(c)
        if isinstance(val, sympy.Float):
            line += "={:10.2g}".format(float(val))
        else:
            line += "={}".format(val)
        if verb:
            line += "={}".format(expr)
        click.echo(line)


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
            print_constants(subs_list, ndim)
        if print_nondims:
            print_ndims(ndim.get_nondims(subs_list))
        if print_scales:
            list_scales(ndim.get_scales(subs_list))
        click.echo('-----')


if(__name__ == "__main__"):
    parse_nondim_params()
