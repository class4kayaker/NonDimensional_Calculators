class PFileLine:
    pass


class CommentLine(PFileLine):
    def __init__(self, comment):
        self.comment = comment


class ControlLine(PFileLine):
    def __init__(self, line, level):
        self.line = line
        self.level = level


class ValueLine(PFileLine):
    def __init__(self, key, value, level):
        self.key = key
        self.value = value
        self.level = level


class ParserNotFound(RuntimeError):
    pass


class ParserCollision(RuntimeError):
    pass


class PFileParser:
    _file_types = {}
    _file_extns = {}

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
        return internal_dec

    @staticmethod
    def parser_by_name(name, fobj):
        try:
            cst = PFileParser._file_types[name]
        except KeyError:
            raise ParserNotFound("No parser for {}".format(name))
        return cst(fobj)

    @staticmethod
    def parser_by_extn(extn, fobj):
        try:
            name = PFileParser._file_extns[extn]
        except KeyError:
            raise ParserNotFound("Extension {} not known".format(extn))
        if not name:
            raise ParserNotFound("Extension {} ambiguous".format(extn))
        return PFileParser.parser_by_name(name, fobj)

    def reset(self):
        raise NotImplementedError()

    def lines(self):
        raise NotImplementedError()

    def typeset_line(line):
        raise NotImplementedError()
