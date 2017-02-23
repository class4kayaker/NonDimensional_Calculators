import re
from sci_parameter_utils.parameter_file import (
    PFileParser, PFileLine)


@PFileParser.register_type("dealIIPRM", "prm")
class PRMParser(PFileParser):
    repl_re = re.compile('{{{([^}]+)}}}')

    @staticmethod
    def lines(fobj):
        def parse_command(cline, lnum, position, comment=""):
            # type: (str, int, List[str], str) -> PFileLine
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
                                     comment=comment,
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
                                     comment=comment,
                                     lnum=lnum,
                                     level=len(position))
                elif(command == 'set'):
                    key, value = remainder.split('=', 1)
                    return PFileLine.keyvalueline(
                        ':'.join(position+[key.strip()]),
                        value.strip(),
                        comment=comment,
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
            comment = ""
            if '#' in line:
                line, comment = line.split('#', 1)
                comment = comment.strip()
                if not line.strip():
                    yield PFileLine.commentline(
                        comment,
                        lnum=linenum)
                    continue

            line = line.strip()

            if(line[-1:] == '\\'):
                if (comment):
                    yield PFileLine.commentline(
                        comment,
                        lnum=linenum)
                parse_line += line[:-1].strip()+' '
                continue

            parse_line += line
            parse_line = parse_line.strip()

            yield parse_command(parse_line, linenum, position, comment)

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
            return '# {}\n'.format(line.comment)
        elif line.ltype == "Control":
            lout = ('{ind:<{ind_s}}{line}'
                    .format(ind='',
                            ind_s=2*line.level,
                            line=line.value))
            if (line.comment):
                lout += " # " + line.comment
            lout += "\n"
            return lout
        elif line.ltype == "KeyValue":
            lout = ('{ind:<{indsp}}set {key} = {value}'
                    .format(ind='',
                            indsp=2*line.level,
                            key=line.value.key.rsplit(':', 1)[-1],
                            value=line.value.value))
            if (line.comment):
                lout += " # " + line.comment
            lout += "\n"
            return lout
        else:
            raise ValueError("Unknown linetype: {}".format(line.ltype))
