import re
from sci_parameter_utils.parameter_file import (
    PFileParser, PFileLine)


@PFileParser.register_type("dealIIPRM", "prm")
class PRMParser(PFileParser):
    repl_re = re.compile('{{{([^}]+)}}}')

    @staticmethod
    def lines(fobj):
        def parse_command(cline, lnum, position):
            if not parse_line:
                return PFileLine(None, None, lnum=lnum)

            try:
                command, remainder = cline.strip().split(' ', 1)
                command = command.strip()
                remainder = remainder.strip()
            except ValueError:
                command, remainder = cline.strip(), None
                command = command.strip()

            try:
                if(command == 'subsection'):
                    position.append(remainder)
                    return PFileLine("Control",
                                     command+' '+remainder,
                                     lnum=lnum,
                                     level=len(position)-1)
                elif(command == 'end'):
                    if(len(position) > 0):
                        position.pop()
                    else:
                        raise ValueError()
                    if remainder:
                        raise ValueError()
                    return PFileLine("Control",
                                     command,
                                     lnum=lnum,
                                     level=len(position))
                elif(command == 'set'):
                    key, value = remainder.split('=', 1)
                    return PFileLine.keyvalueline(
                        ':'.join(position+[key.strip()]),
                        value.strip(),
                        lnum=lnum,
                        level=len(position))
                else:
                    raise ValueError()
            except ValueError:
                errstr = "Line {}: Bad command {}".format(linenum,
                                                          command)
                if remainder:
                    errstr += " with arg {}".format(remainder)
                raise ValueError(errstr)

        position = []
        parse_line = ""
        linenum = 0
        for line in fobj:
            linenum += 1
            # Strip comments
            if '#' in line:
                line, comment = line.split('#', 1)
                yield PFileLine.commentline(
                    comment.strip(),
                    lnum=linenum)
                if not line.strip():
                    continue

            line = line.strip()

            if(line[-1:] == '\\'):
                parse_line += line[:-1].strip()+' '
                continue

            parse_line += line
            parse_line = parse_line.strip()

            yield parse_command(parse_line, linenum, position)

            parse_line = ""

        if parse_line:
            yield parse_command(parse_line, linenum, position)

        if len(position) > 0:
            raise ValueError("Did not exit subsection {}".format(
                ':'.join(position)))

    @staticmethod
    def typeset_line(line):
        if line.ltype is None:
            return '\n'
        elif line.ltype == "Comment":
            return '# {}\n'.format(line.value)
        elif line.ltype == "Control":
            return ('{ind:<{ind_s}}{line}\n'
                    .format(ind='',
                            ind_s=2*line.level,
                            line=line.value))
        elif line.ltype == "KeyValue":
            return ('{ind:<{indsp}}set {key} = {value}\n'
                    .format(ind='',
                            indsp=2*line.level,
                            key=line.value.key.rsplit(':', 1)[-1],
                            value=line.value.value))
        else:
            raise ValueError("Unknown linetype: {}".format(line.ltype))
