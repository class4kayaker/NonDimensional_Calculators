import sympy


_searchers = {}
_extns = {}


def get_searcher_from_extn(extn):
    if extn not in _extns:
        raise NoSearcherFound("Hint {} not known".format(extn))
    searcher_name = _extns[extn]
    if not searcher_name:
        raise NoSearcherFound("Hint {} not known".format(extn))
    return get_searcher(searcher_name)


def get_searcher(name):
    if name not in _searchers:
        raise NoSearcherFound("Searcher {} not known".format(name))
    return _searchers[name]


def register_searcher(cls):
    if cls.name in _searchers:
        raise SearcherCollision(
            "Name {} is already registered".format(cls.name)
        )
    _searchers[cls.name] = cls
    if cls.extn in _extns:
        _extns[cls.extn] = False
    else:
        _extns[cls.extn] = cls.name
    return cls


class NoSearcherFound(Exception):
    pass


class SearcherCollision(Exception):
    pass


class Searcher:
    def __init__(self):
        self.constants = {}

    def add_constant_location(self, var, search):
        if not isinstance(var, sympy.Symbol):
            raise TypeError("Argument var must be a sympy Symbol")
        if not isinstance(search, str):
            raise TypeError("Argument search must be a string")
        if search in self.constants:
            self.constants[search].append(var)
        else:
            self.constants[search] = [var]

    def add_from_dict(self, p_dict):
        if 'constants' in p_dict:
            const_dict = p_dict['constants']
            for k in const_dict:
                try:
                    self.add_constant_location(
                        sympy.symbols(k),
                        const_dict[k]['search']
                    )
                except:
                    raise Exception("Error when adding "
                                    "description for {}".format(k))

    def parse_file(self, paramfile):
        raise NotImplementedError(
            "Parsing not implemented for this parameter file"
        )


@register_searcher
class SearchPRM(Searcher):
    name = "dealIIPRM"
    extn = "prm"

    def parse_file(self, prmfile):
        values = {}
        position = []
        parse_line = ""
        for line in prmfile:
            # Strip comments
            if '#' in line:
                line, _ = line.split('#', 1)

            parse_line += line.strip()

            if(parse_line[-1:] == '\\'):
                continue

            if not parse_line:
                continue

            if(parse_line == 'end'):
                if(len(position) > 0):
                    position.pop()
                else:
                    raise ValueError("Invalid prm file")
                parse_line = ""
                continue

            if ' ' in parse_line:
                command, remainder = parse_line.split(' ', 1)
            else:
                raise ValueError("Bad line: "+parse_line)

            parse_line = ""

            if(command == 'subsection'):
                position.append(remainder.strip())
            elif(command == 'set'):
                key, value = remainder.split('=', 1)
                position.append(key.strip())
                search = ':'.join(position)
                position.pop()
                if search in self.constants:
                    for k in self.constants[search]:
                        sval = value.strip()
                        try:
                            values[k] = float(sval)
                        except:
                            values[k] = sval
            else:
                errmsg = "Bad command {} with arg {}".format(command,
                                                             remainder)
                raise ValueError(errmsg)

        return(values)
