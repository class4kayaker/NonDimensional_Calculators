import sci_parameter_utils.fragment as frag


class TestInputInt:
    def test_create(self):
        name = 'test'
        fmt = "{}"
        elem = frag.TemplateElem.elem_by_type('int',
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt

    def test_create_w_fmt(self):
        name = 'test'
        fmt = "{:g}"
        elem = frag.TemplateElem.elem_by_type('int',
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt
