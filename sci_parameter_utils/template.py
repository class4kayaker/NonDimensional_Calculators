import sympy
import string.Formatter


class Template:
    pass


_elem_types = {}


def register_template_elem_type(etype):
    def internal_dec(cls):
        _elem_types[etype] = cls
        return cls


class InvalidTemplateError(RuntimeError):
    pass


class TemplateElem:
    def get_name(self):
        """Method returning name of template element"""
        raise NotImplementedError()

    def get_dependencies(self):
        """Method returning dependencies of template element, dependency on
        self implies expectation of external definition"""
        raise NotImplementedError()

    def evaluate_dep(self, values):
        """Method returning value of the element suitable for use in final
        file"""
        raise NotImplementedError()

    def evaluate_str(self, values):
        """Method returning string formatting of the element suitable for use
        in final file"""
        raise NotImplementedError()


@register_template_elem_type('int')
class IntElem(TemplateElem):
    def __init__(self, name, fmt):
        self.name = name
        self.fmt = fmt

    def get_name(self):
        return self.name

    def get_dependencies(self):
        return set([self.name])

    def evaluate_dep(self, values):
        return values[self.name]

    def evaluate_str(self, values):
        if self.fmt:
            return self.fmt.format(self.evaluate_dep(values))
        else:
            raise InvalidTemplateError(
                "No formatting provided for element {}".format(self.name))


@register_template_elem_type('float')
class FloatElem(TemplateElem):
    def __init__(self, name, fmt):
        self.name = name
        self.fmt = fmt

    def get_name(self):
        return self.name

    def get_dependencies(self):
        return set([self.name])

    def evaluate_dep(self, values):
        return values[self.name]

    def evaluate_str(self, values):
        if self.fmt:
            return self.fmt.format(self.evaluate_dep(values))
        else:
            raise InvalidTemplateError(
                "No formatting provided for element {}".format(self.name))


@register_template_elem_type('expr')
class ExprElem(TemplateElem):
    def __init__(self, name, fmt, expr):
        self.name = name
        self.expr = sympy.S(expr)
        self.fmt = fmt

    def get_name(self):
        return self.name

    def get_dependencies(self):
        to_ret = set()
        for k in self.expr.atoms(sympy.Symbol):
            to_ret.add(str(k))
        return to_ret

    def evaluate_dep(self, values):
        var_vals = {}
        for k in self.expr.atoms(sympy.Symbol):
            var_vals[k] = values[str(k)]
        return self.expr.subs(var_vals)

    def evaluate_str(self, values):
        if self.fmt:
            return self.fmt.format(self.evaluate_dep(values))
        else:
            raise InvalidTemplateError(
                "No formatting provided for element {}".format(self.name))


@register_template_elem_type('fmt')
class FmtElem(TemplateElem):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def get_name(self):
        return self.name

    def get_dependencies(self):
        return set(string.Formatter.parse(self.expr))

    def evaluate_dep(self, values):
        return self.expr.format(values)

    def evaluate_str(self, values):
        return self.evaluate_dep(values)
