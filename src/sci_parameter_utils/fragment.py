import sympy
import sys
import string
import abc
from six import with_metaclass, raise_from
if sys.version_info.major == 2:
    tr_func = string.maketrans
else:
    tr_func = str.maketrans


def _register_by_type(etype, base_class, store_dict):
    def internal_dec(cls):
        assert issubclass(cls, base_class)
        store_dict[etype] = cls
        return cls
    return internal_dec


def _return_elem_by_type(store_dict, tstr, name, args):
    try:
        cst = store_dict[tstr]
    except KeyError:
        raise InvalidElementError("Unknown type '{}'".format(tstr))
    try:
        return cst(name, **args)
    except TypeError as e:
        raise InvalidElementError(
            "Error constructing element '{}' of type '{}': {}"
            .format(name, tstr, e))


def elems_from_dict(idict, baseElem):
    elems = {}
    for k in idict:
        e = idict[k]
        try:
            tstr = e['type']
            del e['type']
        except KeyError:
            raise InvalidElementError("No type for element '{}'".format(k))
        elems[k] = baseElem.elem_by_type(tstr, k, e)
    return elems


class InvalidElementError(RuntimeError):
    pass


class InvalidInputError(RuntimeError):
    pass


class DependencyError(RuntimeError):
    pass


class TemplateElemSet:
    def __init__(self, elems):
        self.elements = elems
        self._compute_order()
        self._collect_inputs()

    def _compute_order(self):
        searching = set()
        order = []
        for k in self.elements:
            self._search_dep(k, searching, order)
        self.order = order

    def _search_dep(self, k, searching, order):
        if k not in self.elements:
            raise DependencyError("Unknown dependency {}".format(k))
        if k in searching:
            raise DependencyError(
                "Cyclic element dependency including {}".format(k))
        if k in order:
            return
        searching.add(k)
        for d in self.elements[k].get_dependencies():
            self._search_dep(d, searching, order)
        searching.remove(k)
        order.append(k)
        return

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
            try:
                return self.elements[k].validate(v)
            except ValueError as e:
                raise_from(
                    InvalidInputError(
                        "Bad value for {}".format(k)),
                    e)
        else:
            raise InvalidInputError(
                "Invalid input name {}".format(k))

    def compute_values(self, valdict):
        for k in self.order:
            if k in valdict:
                continue
            valdict[k] = self.elements[k].evaluate(valdict)

    def compute_strings(self, valdict):
        self.compute_values(valdict)
        for k in valdict:
            valdict[k] = self.elements[k].do_format(valdict[k])


class TemplateElem(with_metaclass(abc.ABCMeta)):
    _elem_types = {}

    @staticmethod
    def register_type(tstr):
        return _register_by_type(tstr,
                                 TemplateElem,
                                 TemplateElem._elem_types)

    @staticmethod
    def elem_by_type(tstr, name, args):
        return _return_elem_by_type(TemplateElem._elem_types,
                                    tstr,
                                    name,
                                    args)

    @abc.abstractmethod
    def get_name(self):
        """Method returning name of template element"""
        return self.name

    @abc.abstractmethod
    def get_dependencies(self):
        """Method returning dependencies of template element, dependency on
        self implies expectation of external definition"""
        return set()

    @abc.abstractmethod
    def evaluate(self, values):
        """Method returning value of the element suitable for use in final
        file"""
        pass

    def do_format(self, value):
        """Method returning formatted string when given result of evaluate"""
        return str(value)


class InputElem(TemplateElem):
    def __init__(self, name, fmt="{}"):
        self.name = name
        self.fmt = fmt

    def get_name(self):
        return TemplateElem.get_name(self)

    def get_dependencies(self):
        return TemplateElem.get_dependencies(self)

    def evaluate(self, values):
        """Method returning value of the element suitable for use in final
        file"""
        pass

    @abc.abstractmethod
    def validate(self, istr):
        """Do necessary conversion of input string value and raise exceptions
        for invalid values"""
        return str(istr)

    def do_format(self, value):
        return self.fmt.format(value)


@TemplateElem.register_type('int')
class IntElem(InputElem):
    @staticmethod
    def validate(value):
        return int(value)


@TemplateElem.register_type('float')
class FloatElem(InputElem):
    @staticmethod
    def validate(value):
        return float(value)


@TemplateElem.register_type('str')
class StrElem(InputElem):
    def validate(self, value):
        return InputElem.validate(self, value)


class ExprElem(TemplateElem):
    @abc.abstractmethod
    def evaluate(self, values):
        """Method returning value of the element suitable for use in final
        file"""
        pass


@TemplateElem.register_type('expr')
class NExprElem(ExprElem):
    def __init__(self, name, expr, fmt='{}'):
        self.name = name
        self.expr = sympy.S(expr)
        self.fmt = fmt
        if self.name in self.get_dependencies():
            raise DependencyError(
                "Element '{}' cannot be dependent on itself".format(self.name))

    def get_name(self):
        return self.name

    def get_dependencies(self):
        to_ret = set()
        for k in self.expr.atoms(sympy.Symbol):
            to_ret.add(str(k))
        return to_ret

    def evaluate(self, values):
        var_vals = {}
        dep_missing = set()
        for k in self.expr.atoms(sympy.Symbol):
            k_str = str(k)
            try:
                var_vals[k] = values[k_str]
            except KeyError:
                dep_missing.add(k_str)
        if dep_missing:
            raise DependencyError(
                "Missing dependencies {}".format(dep_missing))
        return self.expr.subs(var_vals)

    def do_format(self, value):
        return self.fmt.format(value)


@TemplateElem.register_type('fmt')
class FmtElem(ExprElem):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
        if self.name in self.get_dependencies():
            raise DependencyError(
                "Element '{}' cannot be dependent on itself".format(self.name))

    def get_name(self):
        return self.name

    def get_dependencies(self):
        deps = set()
        for t in string.Formatter().parse(self.expr):
            if t[1]:
                deps.add(t[1])
        return deps

    def evaluate(self, values):
        deps = self.get_dependencies()
        if not deps.issubset(values.keys()):
            raise DependencyError(
                "Missing dependencies {}".format(
                    deps.difference(values.keys())))
        return self.expr.format(**values)


@TemplateElem.register_type('fname')
class FNFmtElem(FmtElem):
    def evaluate(self, values):
        fn_transl = tr_func('./ ', '___')
        return FmtElem.evaluate(self, values).translate(fn_transl)


class SearchElem(with_metaclass(abc.ABCMeta)):
    _elem_types = {}

    @staticmethod
    def register_type(tstr):
        return _register_by_type(tstr, SearchElem, SearchElem._elem_types)

    @staticmethod
    def elem_by_type(tstr, name, args):
        return _return_elem_by_type(SearchElem._elem_types,
                                    tstr,
                                    name,
                                    args)

    @abc.abstractmethod
    def get_name(self):
        return self.name

    @abc.abstractmethod
    def get_key(self):
        return self.key

    @abc.abstractmethod
    def get_value(self, value):
        return value


@SearchElem.register_type('loc')
class LocElem(SearchElem):
    def __init__(self, name, key):
        self.name = name
        self.key = key

    def get_name(self):
        return SearchElem.get_name(self)

    def get_key(self):
        return SearchElem.get_key(self)

    def get_value(self, value):
        return SearchElem.get_value(self, value)
