_templaters = {}
_extns = {}


def get_templater_from_extn(extn):
    if extn not in _extns:
        raise NoTemplaterFound("Hint {} not known".format(extn))
    templater_name = _extns[extn]
    if not templater_name:
        raise NoTemplaterFound("Hint {} not known".format(extn))
    return get_templater_from_extn(templater_name)


def get_templater(name):
    if name not in _templaters:
        raise NoTemplaterFound("Templater {} not known".format(name))
    return _templaters[name]


def register_templater(cls, name, extn):
    if name in _templaters:
        raise TemplaterCollision(
            "Name {} is already registered".format(name)
        )
    _templaters[name] = cls
    if extn in _extns:
        _extns[extn] = False
    else:
        _extns[extn] = name


def register_templater_dec(name, extn):
    def internal_dec(cls):
        register_templater(cls, name, extn)
        return cls
    return internal_dec


class NoTemplaterFound(Exception):
    pass


class TemplaterCollision(Exception):
    pass


class Templater:
    def __init__(self, template):
        self.template = template

    def writeFiles(self, values):
        raise NotImplementedError()
