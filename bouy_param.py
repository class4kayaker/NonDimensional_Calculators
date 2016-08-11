import sys
import sympy


class NonDim:
    def __init__(self):
        self.constants = {}
        self.nondim = {}
        pass

    def add_constant(self, var, descrip):
        if not isinstance(var, sympy.Symbol):
            raise ValueError("Argument var must be a sympy Symbol")
        if var not in self.constants:
            self.constants[var] = descrip
        else:
            raise ValueError(sympy.string(var)+" already exists")

    def add_nondim_param(self, label, expr):
        self.nondim[label] = expr

    def print_constants(self, subs_list, verb=False):
        for v, n in subs_list:
            if v in self.constants:
                tex_var = sympy.latex(v)
                if verb:
                    defn = self.constants[v]
                    print("{:15}= {:13g}: {}".format(tex_var, n, defn))
                else:
                    print("{:15}= {:13}".format(tex_var, n))

    def print_nondim(self, subs_list, verb=False):
        for c in self.nondim:
            expr = self.nondim[c]
            val = expr.subs(subs_list)
            if isinstance(val, sympy.Float):
                if(verb):
                    print("{:5}={:13e}={}".format(c,
                                                  float(val),
                                                  sympy.latex(expr)))
                else:
                    print("{:5}={:13e}".format(c,
                                               float(val)))
            else:
                if(verb):
                    print("{:5}={}={}".format(c, val, sympy.latex(expr)))
                else:
                    print("{:5}={}".format(c, val))


class SearchPRM:
    def __init__(self):
        self.constants = {}

    def add_constant_location(self, var, search):
        if not isinstance(var, sympy.Symbol):
            raise TypeError("Argument var must be a sympy Symbol")
        if not isinstance(search, str):
            raise TypeError("Argument search must be a string")
        if search in self.constants:
            self.constants[search].append(var)
        else:
            self.constants[search] = [var]

    def get_prm_vals(self, prmfile):
        values = {}
        position = []
        parse_line = ""
        for line in prmfile:
            # Strip comments
            c_idx = line.find('#')
            if(c_idx >= 0):
                line = line[:c_idx]

            parse_line += line.strip()

            if(parse_line[-1:] == '\\'):
                continue

            if not parse_line:
                continue

            if(parse_line == 'end'):
                if(len(position) > 0):
                    position.pop()
                else:
                    raise ValueError("Invalid prm file")
                parse_line = ""
                continue

            if ' ' in parse_line:
                command, remainder = parse_line.split(' ', 1)
            else:
                raise ValueError("Bad line: "+parse_line)

            parse_line = ""

            if(command == 'subsection'):
                position.append(remainder.strip())
            elif(command == 'set'):
                key, value = remainder.split('=', 1)
                position.append(key.strip())
                search = ':'.join(position)
                position.pop()
                if search in self.constants:
                    for k in self.constants[search]:
                        sval = value.strip()
                        try:
                            values[k] = float(sval)
                        except:
                            values[k] = sval
            else:
                errmsg = "Bad command {} with arg {}".format(command,
                                                             remainder)
                raise ValueError(errmsg)

        return(values)

BouyParam = NonDim()
BouySearch = SearchPRM()
prm_const_dict = {
    sympy.symbols('mu'):
    ('Viscosity', "Material model:Simple model:Viscosity"),
    sympy.symbols('rho_0'):
    ('Reference density', 'Material model:Simple model:Reference density'),
    sympy.symbols('k'):
    ("Thermal conductivity",
     "Material model:Simple model:Thermal conductivity"),
    sympy.symbols('alpha_v'):
    ('Thermal expansion coefficient',
     "Material model:Simple model:Thermal expansion coefficient"),
    sympy.symbols('c_p'):
    ('Reference specific heat',
     "Material model:Simple model:Reference specific heat"),
    sympy.symbols('Delta_rho'):
    ('Density variation',
     'Material model:Simple model:Density '
     'differential for compositional field 1'),
    sympy.symbols('b'):
    ('Depth', 'Geometry model:Box:Y extent'),
    sympy.symbols('T_h'):
    ('Core temp', 'Boundary temperature model:Box:Bottom temperature'),
    sympy.symbols('T_l'):
    ('Surface temp', 'Boundary temperature model:Box:Top temperature'),
    sympy.symbols('g'):
    ('Gravity', 'Gravity model:Vertical:Magnitude')
}
nondim_dict = {
    'Ra':
    sympy.S('g*rho_0^2*alpha_v*(T_h-T_l)*b^3*c_p/(mu*k)'),
    'B':
    sympy.S('Delta_rho/(rho_0*alpha_v*(T_h-T_l))'),
    'Pr':
    sympy.S('c_p*mu/rho_0')
}
for k in prm_const_dict:
    (defn, loc) = prm_const_dict[k]
    BouyParam.add_constant(k, defn)
    BouySearch.add_constant_location(k, loc)
for k in nondim_dict:
    expr = nondim_dict[k]
    BouyParam.add_nondim_param(k, expr)


for f in sys.argv[1:]:
    print("File {}:\n".format(f))
    with open(f, 'r') as prm_file:
        subs_list = BouySearch.get_prm_vals(prm_file).items()
        print('Values:')
        BouyParam.print_constants(subs_list)
        print('Nondims:')
        BouyParam.print_nondim(subs_list)
    print('-'*10)
