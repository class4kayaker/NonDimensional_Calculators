import abc
from six import add_metaclass


class PFileLine:
    __slots__ = ['lnum', 'ltype', 'level', 'value']

    def __init__(self, ltype, value, level=0, lnum=0):
        assert level >= 0
        assert lnum >= 0
        self.lnum = lnum
        self.ltype = ltype
        self.level = level
        self.value = value

    def __repr__(self):  # pragma nocoverage
        return ("<{}: {} [Line {}]({}): {}>"
                .format(repr(self.__class__),
                        repr(self.ltype),
                        repr(self.lnum),
                        repr(self.level),
                        repr(self.value)))

    def __str__(self):
        return ("<{} [Line {}]({}): {}>"
                .format(self.ltype,
                        self.lnum,
                        self.level,
                        self.value))

    @staticmethod
    def commentline(comment, lnum=0):
        return PFileLine("Comment", comment, lnum=lnum)

    @staticmethod
    def keyvalueline(key, value, level=0, lnum=0):
        return PFileLine("KeyValue",
                         KeyValuePair(key, value),
                         level=level,
                         lnum=lnum)


class KeyValuePair:
    __slots__ = ['key', 'value']

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):  # pragma nocoverage
        return "<{}: {} = {}>".format(self.__class__,
                                      repr(self.key),
                                      repr(self.value))

    def __str__(self):
        return "<{} = {}>".format(self.key,
                                  self.value)


class ParserNotFound(RuntimeError):
    pass


class ParserCollision(RuntimeError):
    pass


@add_metaclass(abc.ABCMeta)
class PFileParser:
    _file_types = {}  # type: Dict[str, PFileParser]
    _file_extns = {}  # type: Dict[str, str]

    @staticmethod
    def register_type(name, extn):
        def internal_dec(cls):
            if name in PFileParser._file_types:
                raise ParserCollision(
                    "Name {} is already registered".format(name))
            PFileParser._file_types[name] = cls
            if extn in PFileParser._file_extns:
                PFileParser._file_extns[extn] = None
            else:
                PFileParser._file_extns[extn] = name
            return cls
        return internal_dec

    @staticmethod
    def parser_by_name(name):
        try:
            cst = PFileParser._file_types[name]
        except KeyError:
            raise ParserNotFound("No parser for {}".format(name))
        return cst

    @staticmethod
    def parser_by_extn(extn):
        try:
            name = PFileParser._file_extns[extn]
        except KeyError:
            raise ParserNotFound("Extension {} not known".format(extn))
        if not name:
            raise ParserNotFound("Extension {} ambiguous".format(extn))
        return PFileParser.parser_by_name(name)

    @staticmethod
    def lines(fobj):
        raise NotImplementedError()  # pragma nocoverage

    @staticmethod
    def typeset_line(line):
        raise NotImplementedError()  # pragma nocoverage
