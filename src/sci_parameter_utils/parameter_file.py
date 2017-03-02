import abc
from six import add_metaclass
try:
    import typing  # noqa: F401
    from typing import Any, Callable, Iterable, Type  # noqa: F401
except:
    pass


class PFileLine:
    """Class to hold a parsed line"""
    __slots__ = ['lnum', 'ltype', 'level', 'value', 'comment']

    def __init__(self, ltype, value, comment="", level=0, lnum=0):
        # type: (str, Any, str, int, int) -> None
        """Initialize line object.

        The object should have sufficient information to recreate a line that
        behaves in an equivalent manner to the original.

        Args:
            ltype (str): Unambiguous indicator for line type. The values
                'Comment' and 'KeyValue' are reserved for particular internal
                use.
            value:  Contents of the line
            comment (str, optional): Any same line comment
            level (int, optional): Nesting level if needed
            lnum (int, optional): Line number
        """
        assert level >= 0
        assert lnum >= 0
        self.lnum = lnum
        self.ltype = ltype
        self.level = level
        self.value = value
        self.comment = comment

    def __repr__(self):  # pragma nocoverage
        # type: () -> str
        return (("<{0.__class__!r}: "
                 "{0.ltype!r} [Line {0.lnum}]({0.level}): "
                 "{0.value!r} # {0.comment!r}>")
                .format(self))

    def __str__(self):
        # type: () -> str
        return (("<{0.ltype!s} [Line {0.lnum}]({0.level}): "
                 "{0.value!s} # {0.comment!s}>")
                .format(self))

    @staticmethod
    def commentline(comment, lnum=0, level=0):
        # type: (str, int, int) -> PFileLine
        """Create a comment line

        Args:
            comment (str): Comment string
            lnum (int, optional): Line number
            level (int, optional): Nesting level

        Returns:
            :py:class:`~.PFileLine`: Line object of standard form for a comment
                line
        """
        return PFileLine("Comment", None, comment=comment,
                         level=level, lnum=lnum)

    @staticmethod
    def keyvalueline(key, value, level=0, lnum=0, comment=""):
        # type: (str, str, int, int, str) -> PFileLine
        """Create a key-value pair line

        Args:
            key (str): Parameter key in a unambiguous form
            value (str): Value of given parameter
            level (int, optional): Nesting level
            lnum (int, optional): Line number
            comment (str, optional): Same line comment if any

        Returns:
            :py:class:`~.PFileLine`: Line object of standard form for a comment
                line
        """
        return PFileLine("KeyValue",
                         KeyValuePair(key, value),
                         comment=comment,
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
        return "<{0.__class__!r}: {0.key!r} = {0.value!r}>".format(self)

    def __str__(self):
        # type: () -> str
        return "<{0.key!s} = {0.value!s}>".format(self)


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
        """Decorator to register parser.

        Args:
            name (str): Unique identifier for parameter file type
            extn (str): Expected extension for parameter file type
        """
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
        """Get parser by unique identifier.

        Args:
            name (str): Unique name for parser

        Returns:
            :class:`PFileParser`: Appropriate parser
        """
        try:
            cst = PFileParser._file_types[name]
        except KeyError:
            raise ParserNotFound("No parser for {}".format(name))
        return cst

    @staticmethod
    def parser_by_extn(extn):
        # type: (str) -> Type[PFileParser]
        """Get parser by extension if unique.

        Args:
            extn (str): Extension of the parameter file.

        Returns:
            Type[PFileParser]: Appropriate parser
        """
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
        """Generator returning parsed lines from the file.

        Args:
            fobj (str): File to read from.

        Yields:
            :py:class:`~.PFileLine`: The next line from the given file.
        """
        raise NotImplementedError()  # pragma nocoverage

    @staticmethod
    def typeset_line(line):
        # type: (PFileLine) -> str
        """Funcition that will typeset a line parsed from the same parser.

        Args:
            line (:py:class:`~.PFileLine`): Line to be typeset

        Return:
            str: String to be written to the file, should include newline.
        """
        raise NotImplementedError()  # pragma nocoverage
