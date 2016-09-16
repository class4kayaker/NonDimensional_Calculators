import sympy


class NonDim:
    """
    Class to handle the parameters of a problem
    """
    constants = {}
    nondim = {}
    scales = {}

    def add_from_dict(self, p_dict):
        """
        Get parameter information from provided dicitonary with known layout
        """
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
                try:
                    self.add_nondim_param(
                        k,
                        sympy.S(nondim_dict[k])
                    )
                except:
                    raise Exception("Error when adding {}".format(k))

        if 'scales' in p_dict:
            scales_dict = p_dict['scales']
            for k in scales_dict:
                try:
                    self.add_scale(
                        k,
                        sympy.S(scales_dict[k])
                    )
                except:
                    raise Exception("Error when adding {}".format(k))

    def add_constant(self, var, descrip):
        """
        Add a constant and description
        """
        if not isinstance(var, sympy.Symbol):
            raise ValueError("Argument var must be a sympy Symbol")
        if var not in self.constants:
            self.constants[var] = descrip
        else:
            raise ValueError(sympy.string(var)+" already exists")

    def add_nondim_param(self, label, expr):
        """
        Add a non-dimensional parameter and expression
        """
        self.nondim[label] = expr

    def add_scale(self, name, expr):
        """
        Add a unit scale by expression
        """
        self.scales[name] = expr

    def get_const_desc(self, v):
        """
        Get a constant by sympy variable
        """
        if v in self.constants:
            return self.constants[v]
        return None

    def write_consts(self, ofile, subs, verb=False):
        """
        Write constants to ofile stream
        """
        for v, n in subs.items():
            tex_var = sympy.latex(v)
            defn = self.get_const_desc(v)
            ofile.write("   {:15}= {:13g}".format(tex_var, n))
            if verb and defn:
                ofile.write(": {}".format(defn))
            ofile.write("\n")

    def get_nondims(self, subs):
        """
        Return list of non-dimensional parameters
        """
        ndims = []
        for c in self.nondim:
            expr = self.nondim[c]
            val = expr.subs(subs)
            ndims.append((c, val, expr))
        return ndims

    def write_nondim(self, ofile, subs, verb=False):
        """
        Write nondimensional parameters to ofile stream
        """
        for c, val, expr in self.get_nondims(subs):
            ofile.write("   {:5}".format(c))
            if isinstance(val, sympy.Float):
                ofile.write("={:10.2g}".format(float(val)))
            else:
                ofile.write("={}".format(val))
            if verb:
                ofile.write("={}".format(expr))
            ofile.write("\n")

    def get_scales(self, subs):
        """
        Return list of unit scales
        """
        scales = []
        for c in self.scales:
            expr = self.scales[c]
            val = expr.subs(subs)
            scales.append((c, val, expr))
        return scales

    def write_scales(self, ofile, subs, verb=False):
        """
        Write unit scales to ofile stream
        """
        for c, val, expr in self.get_scales(subs):
            ofile.write("   {:15}".format(c))
            if isinstance(val, sympy.Float):
                ofile.write("={:10.2g}".format(float(val)))
            else:
                ofile.write("={}".format(val))
            if verb:
                ofile.write("={}".format(expr))
            ofile.write("\n")
