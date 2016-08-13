import sympy


class NonDim:
    def __init__(self):
        self.constants = {}
        self.nondim = {}
        pass

    def add_from_dict(self, p_dict):
        if 'constants' in p_dict:
            const_dict = p_dict['constants']
            for k in const_dict:
                try:
                    self.add_constant(
                        sympy.symbols(k),
                        const_dict[k]['description']
                    )
                except:
                    raise Exception("Error when adding "
                                    "description for {}".format(k))
        if 'nondims' in p_dict:
            nondim_dict = p_dict['nondims']
            for k in nondim_dict:
                self.add_nondim_param(
                    k,
                    sympy.S(nondim_dict[k])
                )

    def add_constant(self, var, descrip):
        if not isinstance(var, sympy.Symbol):
            raise ValueError("Argument var must be a sympy Symbol")
        if var not in self.constants:
            self.constants[var] = descrip
        else:
            raise ValueError(sympy.string(var)+" already exists")

    def add_nondim_param(self, label, expr):
        self.nondim[label] = expr

    def get_const_desc(self, v):
        if v in self.constants:
            return self.constants[v]
        return None

    def get_nondims(self, subs):
        ndims = []
        for c in self.nondim:
            expr = self.nondim[c]
            val = expr.subs(subs)
            ndims.append((c, val, expr))
        return ndims
