import pytest
import sci_parameter_utils.fragment as frag


@pytest.mark.parametrize("tstr", [
    'int',
    'float',
    'str'
])
class TestInputElems:
    def test_create(self, tstr):
        name = 'test'
        fmt = "{}"
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt
        assert elem.get_dependencies() == set()

    def test_create_w_fmt(self, tstr):
        name = 'test'
        fmt = "{:g}"
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt
        assert elem.get_dependencies() == set()


@pytest.mark.parametrize("tstr,expr,deps", [
    ('expr', 'a*b+c', set(['a', 'b', 'c'])),
    ('fmt', '{a} {b} {c}', set(['a', 'b', 'c'])),
    ('fname', '{a} {b} {c}', set(['a', 'b', 'c'])),
])
class TestExprElems:
    def test_create(self, tstr, expr, deps):
        name = 'test'
        args = {
            'expr': expr
        }
        elem = frag.TemplateElem.elem_by_type(tstr,
                                              name,
                                              args,
                                              )

        assert elem.name == name
        assert elem.get_dependencies() == deps
