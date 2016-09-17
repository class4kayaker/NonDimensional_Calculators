import pytest
import sci_parameter_utils.fragment as frag
import sympy


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
