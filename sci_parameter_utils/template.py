import sci_parameter_utils.fragment


class TemplateElemSet:
    def __init__(self, idict):
        self.elements = (
            sci_parameter_utils.fragment.
            elems_from_dict(idict, sci_parameter_utils.fragment.TemplateElem))
        self._compute_order()
        self._collect_inputs()

    def _collect_inputs(self):
        self.inputs = set()
        for k in self.elements:
            e = self.elements[k]
            if isinstance(e, sci_parameter_utils.fragment.InputElem):
                self.inputs.add(k)

    def get_inputs(self):
        return self.inputs

    def validate(self, k, v):
        if k in self.inputs:
            return self.elements[k].validate(v)
        else:
            raise sci_parameter_utils.fragment.InvalidInputError(
                "Invalid input name {}".format(k))

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


class InvalidTemplateError(RuntimeError):
    pass
