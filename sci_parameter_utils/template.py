import sympy
import string


class TemplateElemSet:
    def __init__(self, idict):
        self.elements = {}
        for k in idict:
            e = idict[k]
            e['name'] = k
            try:
                tstr = e['type']
                del e['type']
            except KeyError:
                raise InvalidTemplateError("No type for element {}".format(k))
            cst = elem_constructor_by_type(tstr)
            try:
                self.elements[k] = cst(**e)
            except TypeError as e:
                raise InvalidTemplateError(
                    "Error constructing element {} of type {}: {}"
                    .format(k, tstr, e))
        self._compute_order()
        self._collect_inputs()

    def _collect_inputs(self):
        self.inputs = set()
        for k in self.elements:
            e = self.elements[k]
            if isinstance(e, InputElem):
                self.inputs.add(k)

    def get_inputs(self):
        return self.inputs

    def validate(self, k, v):
        if k in self.inputs:
            return self.elements[k].validate(v)
        else:
            raise InvalidInputError("Invalid input name {}".format(k))

    def compute_strs(self, valdict):
        for k in self.order:
            if k in valdict:
                continue
            valdict[k] = self.elements[k].evaluate(valdict)
        for k in valdict:
            valdict[k] = self.elements[k].do_format(valdict[k])

    def _compute_order(self):
        searching = set()
        order = []
        for k in self.elements:
            self._search_dep(k, searching, order)
        self.order = order

    def _search_dep(self, k, searching, order):
        if k not in self.elements:
            raise InvalidTemplateError("Unknown dependency {}".format(k))
        if k in searching:
            raise InvalidTemplateError(
                "Cyclic element dependency including {}".format(k))
        if k in order:
            return
        searching.add(k)
        for d in self.elements[k].get_dependencies():
            self._search_dep(d, searching, order)
        searching.remove(k)
        order.append(k)
        return


_elem_types = {}


def register_template_elem_type(etype):
    def internal_dec(cls):
        _elem_types[etype] = cls
        return cls
    return internal_dec


def elem_constructor_by_type(tstr, **args):
    if tstr in _elem_types:
        return _elem_types[tstr]
    else:
        raise InvalidTemplateError('Unknown type {}'.format(tstr))


class InvalidTemplateError(RuntimeError):
    pass


class InvalidInputError(RuntimeError):
    pass


class TemplateElem:
    def get_name(self):
        """Method returning name of template element"""
        raise NotImplementedError()

    def get_dependencies(self):
        """Method returning dependencies of template element, dependency on
        self implies expectation of external definition"""
        raise NotImplementedError()

    def evaluate(self, values):
        """Method returning value of the element suitable for use in final
        file"""
        raise NotImplementedError()

    def do_format(self, value):
        """Method returning formatted string when given result of evaluate"""
        return str(value)


class InputElem(TemplateElem):
    def __init__(self, name, fmt="{}"):
        self.name = name
        self.fmt = fmt

    def get_name(self):
        return self.name

    def get_dependencies(self):
        return set()

    def validate(self, istr):
        raise NotImplementedError()

    def do_format(self, value):
        return self.fmt.format(value)


@register_template_elem_type('int')
class IntElem(InputElem):
    def validate(self, istr):
        try:
            return int(istr)
        except ValueError:
            raise InvalidInputError("Bad value for {}".format(self.name))


@register_template_elem_type('float')
class FloatElem(InputElem):
    def validate(self, istr):
        try:
            return float(istr)
        except ValueError:
            raise InvalidInputError("Bad value for {}".format(self.name))


@register_template_elem_type('str')
class StrElem(InputElem):
    def validate(self, istr):
        try:
            return str(istr)
        except ValueError:
            raise InvalidInputError("Bad value for {}".format(self.name))


@register_template_elem_type('expr')
class ExprElem(TemplateElem):
    def __init__(self, name, expr, fmt='{}'):
        self.name = name
        self.expr = sympy.S(expr)
        self.fmt = fmt
        if self.name in self.get_dependencies():
            raise InvalidTemplateError(
                "Element {} cannot be dependent on itself".format(self.name))

    def get_name(self):
        return self.name

    def get_dependencies(self):
        to_ret = set()
        for k in self.expr.atoms(sympy.Symbol):
            to_ret.add(str(k))
        return to_ret

    def evaluate(self, values):
        var_vals = {}
        for k in self.expr.atoms(sympy.Symbol):
            var_vals[k] = values[str(k)]
        return self.expr.subs(var_vals)

    def do_format(self, value):
        return self.fmt.format(value)


@register_template_elem_type('fmt')
class FmtElem(TemplateElem):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        if self.name in self.get_dependencies():
            raise InvalidTemplateError(
                "Element {} cannot be dependent on itself".format(self.name))

    def get_name(self):
        return self.name

    def get_dependencies(self):
        deps = set()
        for t in string.Formatter().parse(self.expr):
            if t[1]:
                deps.add(t[1])
        return deps

    def evaluate(self, values):
        return self.expr.format(values)


@register_template_elem_type('fname')
class FNFmtElem(FmtElem):
    def evaluate(self, values):
        fn_transl = string.maketrans('./', '__')
        return self.expr.format(**values).translate(fn_transl)
