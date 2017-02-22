import abc
from six import add_metaclass
try:
    import typing  # noqa: F401
    from typing import Any, Callable, Iterable, Type  # noqa: F401
except:
    pass


class PFileLine:
    __slots__ = ['lnum', 'ltype', 'level', 'value']

    def __init__(self, ltype, value, level=0, lnum=0):
        # type: (str, Any, int, int) -> None
        assert level >= 0
        assert lnum >= 0
        self.lnum = lnum
        self.ltype = ltype
        self.level = level
        self.value = value

    def __repr__(self):  # pragma nocoverage
        # type: () -> str
        return (("<{0.__class__!r}: "
                 "{0.ltype} [Line {0.lnum}]({0.level}): "
                 "{0.value!r}>")
                .format(self))

    def __str__(self):
        # type: () -> str
        return (("<{0.ltype} [Line {0.lnum}]({0.level}): "
                 "{0.value!s}>")
                .format(self))

    @staticmethod
    def commentline(comment, lnum=0, level=0):
        # type: (str, int, int) -> PFileLine
        return PFileLine("Comment", comment, level=level, lnum=lnum)

    @staticmethod
    def keyvalueline(key, value, level=0, lnum=0):
        # type: (str, str, int, int) -> PFileLine
        return PFileLine("KeyValue",
                         KeyValuePair(key, value),
                         level=level,
                         lnum=lnum)


class KeyValuePair:
    __slots__ = ['key', 'value']

    def __init__(self, key, value):
        # type: (str, str) -> None
        self.key = key
        self.value = value

    def __repr__(self):  # pragma nocoverage
        # type: () -> str
        return "<{0.__class__!r}: {0.key} = {0.value}>".format(self)

    def __str__(self):
        # type: () -> str
        return "<{0.key} = {0.value}>".format(self)


class ParserNotFound(Exception):
    pass


class ParserCollision(Exception):
    pass


@add_metaclass(abc.ABCMeta)
class PFileParser:
    _file_types = {}  # type: Dict[str, typing.Type[PFileParser]]
    _file_extns = {}  # type: Dict[str, str]

    @staticmethod
    def register_type(name, extn):
        # type: (str, str) -> Callable[[Type[PFileParser]], Type[PFileParser]]
        def internal_dec(cls):
            # type: (Type[PFileParser]) -> Type[PFileParser]
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
        # type: (str) -> Type[PFileParser]
        try:
            cst = PFileParser._file_types[name]
        except KeyError:
            raise ParserNotFound("No parser for {}".format(name))
        return cst

    @staticmethod
    def parser_by_extn(extn):
        # type: (str) -> Type[PFileParser]
        try:
            name = PFileParser._file_extns[extn]
        except KeyError:
            raise ParserNotFound("Extension {} not known".format(extn))
        if not name:
            raise ParserNotFound("Extension {} ambiguous".format(extn))
        return PFileParser.parser_by_name(name)

    @staticmethod
    def lines(fobj):
        # type: (Any) -> Iterable[PFileLine]
        raise NotImplementedError()  # pragma nocoverage

    @staticmethod
    def typeset_line(line):
        # type: (PFileLine) -> str
        raise NotImplementedError()  # pragma nocoverage
