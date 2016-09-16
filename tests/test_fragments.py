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
