import re

_templaters = {}
_extns = {}


def get_templater_from_extn(extn):
    if extn not in _extns:
        raise NoTemplaterFound("Hint {} not known".format(extn))
    templater_name = _extns[extn]
    if not templater_name:
        raise NoTemplaterFound("Hint {} not known".format(extn))
    return get_templater(templater_name)


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


class UnknownElemError(RuntimeError):
    pass


class Templater:
    def __init__(self):
        self.repl_re = re.compile('{{{([^}]+)}}}')

    def replace(self, istr, values):
        def repl_fn(match):
            k = match.group(1)
            if k not in values:
                raise UnknownElemError(
                    "No element {} supplied".format(k))
            return values[k]
        return self.repl_re.sub(repl_fn, istr)

    def template_file(self, ifile, ofile, values):
        raise NotImplementedError()


@register_templater_dec("dealIIPRM", "prm")
class TemplatePRM(Templater):
    """Class for templating dealII files"""
    def get_fn_suggest(self, prmfile):
        sugg_re = re.compile('#\s+FN:\s+(\S+)')
        for line in prmfile:
            match = sugg_re.search(line)
            if match:
                fn_suggest = match.group(1)
                return fn_suggest

    def template_file(self, prmfile, ofile, values):
        indent = 0
        parse_line = ""
        for line in prmfile:
            # Strip comments
            if '#' in line:
                line, comment = line.split('#', 1)
                ofile.write('#'+comment+'\n')

            parse_line += line.strip()

            if(parse_line[-1:] == '\\'):
                continue

            if not parse_line:
                continue

            if(parse_line == 'end'):
                if(indent > 0):
                    indent -= 1
                else:
                    raise ValueError("Invalid prm file")
                parse_line = ""
                ofile.write(indent*'  '+'end\n')
                continue

            if ' ' in parse_line:
                command, remainder = parse_line.split(' ', 1)
            else:
                raise ValueError("Bad line: "+parse_line)

            parse_line = ""

            if(command == 'subsection'):
                ofile.write(indent*'  '+'subsection '+remainder+'\n')
                indent += 1
            elif(command == 'set'):
                key, value = remainder.split('=', 1)
                ofile.write(indent*'  ' +
                            'set '+key+' = '+self.replace(value, values)+'\n')
            else:
                errmsg = "Bad command {} with arg {}".format(command,
                                                             remainder)
                raise ValueError(errmsg)
