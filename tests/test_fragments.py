import sci_parameter_utils.fragment as frag


class TestInputInt:
    tstr = 'int'

    def test_create(self):
        name = 'test'
        fmt = "{}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt

    def test_create_w_fmt(self):
        name = 'test'
        fmt = "{:g}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt


class TestInputFloat:
    tstr = 'float'

    def test_create(self):
        name = 'test'
        fmt = "{}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt

    def test_create_w_fmt(self):
        name = 'test'
        fmt = "{:g}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt


class TestInputStr:
    tstr = 'str'

    def test_create(self):
        name = 'test'
        fmt = "{}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt

    def test_create_w_fmt(self):
        name = 'test'
        fmt = "{:g}"
        elem = frag.TemplateElem.elem_by_type(self.tstr,
                                              name,
                                              {'fmt': fmt}
                                              )

        assert elem.name == name
        assert elem.fmt == fmt
