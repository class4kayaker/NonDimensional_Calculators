import pytest
import sci_parameter_utils.fragment as frag


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

        assert elem.name == name
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


@pytest.mark.parametrize("tstr,args,value,output", [
    ('loc', {}, 'test', 'test'),
    ('loc', {}, 'test2', 'test2'),
])
def test_searchers(tstr, args, value, output):
    name = 'test'
    args['key'] = 'test'
    elem = frag.SearchElem.elem_by_type(tstr,
                                        name,
                                        args,)

    assert elem.get_value(value) == output
