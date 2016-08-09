import sys
import re
import sympy


class BouyParam:
    def __init__(self):
        self.constants = {}
        self.constants[sympy.symbols('mu')] = "Viscosity"
        self.constants[sympy.symbols('rho_0')] = 'Reference density'
        self.constants[sympy.symbols('k')] = "Thermal conductivity"
        self.constants[sympy.symbols('alpha_v')] = (
            'Thermal expansion coefficient'
        )
        self.constants[sympy.symbols('c_p')] = 'Reference specific heat'
        self.constants[sympy.symbols('Delta_rho')] = (
            'Density differential for compositional field 1'
        )
        self.constants[sympy.symbols('b')] = 'Y extent'
        self.constants[sympy.symbols('T_h')] = 'Bottom temperature'
        self.constants[sympy.symbols('T_l')] = 'Top temperature'
        self.constants[sympy.symbols('g')] = 'Magnitude'

        self.values = {}
        for k in self.constants:
            self.values[k] = float('nan')

        self.nondim = {}
        self.nondim['Ra'] = sympy.S(
            'g*rho_0^2*alpha_v*(T_h-T_l)*b^3*c_p/(mu*k)'
        )
        self.nondim['B'] = sympy.S('Delta_rho/(rho_0*alpha_v*(T_h-T_l))')
        self.nondim['Pr'] = sympy.S('c_p*mu/rho_0')

    def print_values(self):
        for k in self.values:
            print "{:15}={:13g}".format(sympy.latex(k), self.values[k])

    def print_nondim(self):
        for c in self.nondim:
            expr = self.nondim[c]
            val = expr.subs(self.values.items())
            if isinstance(val, sympy.Float):
                print "{:5}={:13g}={}".format(c, float(val), sympy.latex(expr))
            else:
                print "{:5}={:13}={}".format(c, float(val), sympy.latex(expr))

    def set_value(self, var, value):
        if var not in self.values:
            raise ValueError("{} not allowed".format(var))

        self.values[var] = value

    def read_params(self, fstr):
        for line in fstr:
            for k in self.constants:
                reexpr = '\\s+set\\s+{}\\s+=\\s+([\d.Ee-]+)'.format(
                    self.constants[k]
                )
                regex = re.compile(reexpr)
                match = regex.match(line)
                if match is not None:
                    try:
                        self.values[k] = float(match.groups()[0])
                    except:
                        pass


class ParsePRM:
    def __init__(self):
        self.contents = {}


for f in sys.argv[1:]:
    prms = BouyParam()
    prms.read_params(open(f, 'r'))
    print 'Values:'
    prms.print_values()
    print "Nondims"
    prms.print_nondim()
