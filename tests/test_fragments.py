import pytest
import sci_parameter_utils.fragment as frag
import sympy
import copy


@pytest.mark.parametrize("tstr,name,args,error", [
    ('invalid', 'test', {}, "Unknown type 'invalid'"),
    ('int', 'test', {'bad_arg': 1}, "Error constructing element "
     "'test' of type 'int': __init__() got an unexpected keyword "
     "argument 'bad_arg'"),
])
def test_invalid_types(tstr, name, args, error):
    with pytest.raises(frag.InvalidElementError) as excinfo:
        frag.TemplateElem.elem_by_type(tstr,
                                       name,
                                       args
                                       )

    assert error == str(excinfo.value)


@pytest.mark.parametrize("tstr,name", [
    ('int', 'test'),
    ('int', 'test2'),
    ('float', 'test'),
    ('float', 'test2'),
    ('str', 'test'),
    ('str', 'test2')
])
class TestInputElems:
    def test_create(self, tstr, name):
        def_fmt = "{}"
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == def_fmt
        assert elem.get_dependencies() == set()

    @pytest.mark.parametrize("fmt", [
        '{:}',
        '{:g}',
    ])
    def test_create_w_fmt(self, tstr, name, fmt):
        name = 'test'
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.get_name() == name
        assert elem.fmt == fmt
        assert elem.get_dependencies() == set()


@pytest.mark.parametrize("tstr,name,expr,deps", [
    ('expr', 'test', 'a*b+c', set(['a', 'b', 'c'])),
    ('expr', 'test2', 'd+b+c', set(['d', 'b', 'c'])),
    ('fmt', 'test', '{a} {b} {c}', set(['a', 'b', 'c'])),
    ('fmt', 'test2', '{c} {b} {d}', set(['c', 'b', 'd'])),
    ('fname', 'test', '{a} {b} {c}', set(['a', 'b', 'c'])),
    ('fname', 'test2', '{f} {b} {w}', set(['f', 'b', 'w'])),
])
class TestExprElems:
    def test_create(self, tstr, name, expr, deps):
        args = {
            'expr': expr
        }
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              args,
                                              )

        assert elem.get_name() == name
        assert elem.get_dependencies() == deps


@pytest.mark.parametrize("tstr,name,args,key", [
    ('loc', 'test', {}, 'CFL'),
    ('loc', 'test2', {}, 'CFL:Test:key'),
])
class TestSearchElems:
    def test_create(self, tstr, name, args, key):
        assert 'key' not in args
        args['key'] = key
        elem = frag.SearchElem.elem_by_type(tstr,
                                            name,
                                            args,)

        assert elem.name == name
        assert elem.get_key() == key


@pytest.mark.parametrize("tstr,value,result,fmt", [
    ('int', 1, 1, '1'),
    ('int', '1', 1, '1'),
    ('float', 3.4, 3.4, '3.4'),
    ('float', 3, 3.0, '3.0'),
    ('float', '3.4', 3.4, '3.4'),
    ('str', '3.4', '3.4', '3.4'),
])
def test_valid_values(tstr, value, result, fmt):
    name = 'test'
    elem = frag.TemplateElem.elem_by_type(tstr,
                                          name,
                                          {}
                                          )

    v = elem.validate(value)
    assert v == result
    assert elem.do_format(v) == fmt


@pytest.mark.parametrize("tstr,value", [
    ('int', 'a'),
    ('int', '3.4'),
    ('float', 'a'),
])
def test_invalid_values(tstr, value):
    name = 'test'
    elem = frag.TemplateElem.elem_by_type(tstr,
                                          name,
                                          {}
                                          )
    with pytest.raises(ValueError):
        elem.validate(value)


@pytest.mark.parametrize("tstr,expr,idict,interm,fmt", [
    ('expr', 'a', {'a': 5}, 5, '5'),
    ('expr', 'a*b', {'a': 5, 'b': 2}, 10, '10'),
    ('fmt', '{a:}', {'a': 5}, '5', '5'),
    ('fmt', '{a:} {b:}', {'a': 5, 'b': 2}, '5 2', '5 2'),
    ('fname', '{a:}', {'a': 5}, '5', '5'),
    ('fname', '{a:}./ {b:}', {'a': 5, 'b': 2}, '5___2', '5___2'),
])
def test_expressions(tstr, expr, idict, interm, fmt):
    name = 'test'
    args = {'expr': expr}
    elem = frag.TemplateElem.elem_by_type(tstr,
                                          name,
                                          args,
                                          )

    out = elem.evaluate(idict)
    assert out == interm
    assert fmt == elem.do_format(out)


@pytest.mark.parametrize("tstr,name,expr,etype,error", [
    ('expr', 'a', 'a', frag.DependencyError,
     "Element 'a' cannot be dependent on itself"),
    ('expr', 'test', 'a***b', sympy.SympifyError, ""),
    ('fmt', 'a', '{a}', frag.DependencyError,
     "Element 'a' cannot be dependent on itself"),
])
def test_invalid_expressions(tstr, name, expr, etype, error):
    args = {'expr': expr}
    with pytest.raises(etype) as excinfo:
        frag.TemplateElem.elem_by_type(tstr,
                                       name,
                                       args,
                                       )
    if error:
        assert error == str(excinfo.value)


@pytest.mark.parametrize("tstr,expr,idict,missing", [
    ('expr', 'a', {}, set(['a'])),
    ('expr', 'b', {'c': 1}, set(['b'])),
    ('fmt', '{a}', {}, set(['a'])),
    ('fmt', '{b}', {'c': 1}, set(['b'])),
    ('fname', '{a}', {}, set(['a'])),
    ('fname', '{b}', {'c': 1}, set(['b'])),
])
def test_missing_dependent_expressions(tstr, expr, idict, missing):
    name = 'test'
    args = {'expr': expr}
    elem = frag.TemplateElem.elem_by_type(tstr,
                                          name,
                                          args,
                                          )
    with pytest.raises(frag.DependencyError) as excinfo:
        elem.evaluate(idict)

    assert str(excinfo.value) == "Missing dependencies {}".format(missing)


@pytest.mark.parametrize("tstr,name,key,args,value,output", [
    ('loc', 'test', 'key', {}, 'test', 'test'),
    ('loc', 'test', 'key', {}, 'test2', 'test2'),
])
def test_searchers(tstr, name, key, args, value, output):
    args['key'] = key
    elem = frag.SearchElem.elem_by_type(tstr,
                                        name,
                                        args,)

    assert elem.get_name() == name
    assert elem.get_key() == key
    assert elem.get_value(value) == output


@pytest.mark.parametrize("idict", [
    {'a': {'type': 'b'}},
    {'a': {'type': 'b'}, 'b': {'type': 'c', 'test': 'd'}}
])
def test_create_from_dict(idict, monkeypatch):
    @staticmethod
    def test_fn(tstr, name, args):
        assert name in idict
        assert 'name' not in args
        assert 'type' not in args
        assert set(idict[name].keys()) == set(['type']).union(args.keys())
        for k in args:
            assert idict[name][k] == args[k]

    monkeypatch.setattr(frag.TemplateElem, 'elem_by_type', test_fn)
    frag.elems_from_dict(copy.deepcopy(idict), frag.TemplateElem)


@pytest.mark.parametrize("idict,error", [
    ({'a': {'r': 'b'}}, "No type for element 'a'"),
    ({'a': {'type': 'b'}, 'b': {'l': 'c', 'test': 'd'}},
     "No type for element 'b'")
])
def test_no_type_create_from_dict(idict, error, monkeypatch):
    @staticmethod
    def test_fn(tstr, name, args):
        pass

    monkeypatch.setattr(frag.TemplateElem, 'elem_by_type', test_fn)
    with pytest.raises(frag.InvalidElementError) as excinfo:
        frag.elems_from_dict(copy.deepcopy(idict), frag.TemplateElem)

    assert error == str(excinfo.value)


class DElem(frag.TemplateElem):
    def __init__(self, name, deps):
        self.name = name
        self.deps = deps

    def get_name(self):
        return frag.TemplateElem.get_name(self)

    def get_dependencies(self):
        return self.deps

    def evaluate(self, values):
        for k in self.deps:
            assert values[k] == k
        return self.name

    def do_format(self, value):
        return '{}: {}'.format(self.name, value)


class IElem(DElem, frag.InputElem):
    def __init__(self, name):
        DElem.__init__(self, name, set())

    def validate(self, value):
        return (self.name, frag.InputElem.validate(self, value))


@pytest.fixture
def frag_elemset(request):
    ins, dep_dict = request.param
    edict = {}
    # Setup
    for i in ins:
        edict[i] = IElem(i)
    for k in dep_dict:
        edict[k] = DElem(k, dep_dict[k])
    return (ins, dep_dict, edict)


@pytest.mark.parametrize("frag_elemset", [
    (set("abc"), {'w': set('ac'), 't': set('aw')}),
], indirect=['frag_elemset'])
def test_elemset(frag_elemset):
    ins, _, edict = frag_elemset
    eset = frag.TemplateElemSet(edict)
    assert eset.get_inputs() == ins
    vals = {}
    for i in ins:
        for v in ['a', 'b']:
            assert (i, str(v)) == eset.validate(i, v)
        vals[i] = i

    vals_str = copy.deepcopy(vals)
    eset.compute_values(vals)
    vals_str_cpy = copy.deepcopy(vals)
    eset.compute_strings(vals_str)
    eset.compute_strings(vals_str_cpy)
    assert vals.keys() == vals_str.keys()
    assert vals_str.keys() == vals_str_cpy.keys()
    for k in vals:
        assert k == vals[k]
        assert vals_str[k] == '{}: {}'.format(k, k)
        assert vals_str_cpy[k] == '{}: {}'.format(k, k)


def test_fail_input_elemset(monkeypatch):
    def test_fn(value):
        raise ValueError()
    k = 'a'
    k2 = 'b'
    assert not k == k2
    v = 'b'
    el = IElem(k)
    monkeypatch.setattr(el, 'validate', test_fn)
    edict = {
        k: el
    }
    eset = frag.TemplateElemSet(edict)
    with pytest.raises(frag.InvalidInputError) as excinfo:
        eset.validate(k2, v)

    assert str(excinfo.value).startswith('Invalid input name')

    with pytest.raises(frag.InvalidInputError) as excinfo:
        eset.validate(k, v)

    assert str(excinfo.value).startswith('Bad value for')


@pytest.mark.parametrize("frag_elemset,exc,error", [
    ((set("abc"), {'w': set('dc'), 't': set('aw')}),
     frag.DependencyError, "Unknown dependency"),
    ((set("abc"), {'w': set('tc'), 't': set('aw')}),
     frag.DependencyError, 'Cyclic element dependency including')
], indirect=['frag_elemset'])
def test_elemset_depfail(frag_elemset, exc, error):
    ins, _, edict = frag_elemset
    with pytest.raises(exc) as excinfo:
        frag.TemplateElemSet(edict)

    if error:
        assert str(excinfo.value).startswith(error)
