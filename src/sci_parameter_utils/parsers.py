from sci_parameter_utils.parameter_file import (
    PFileParser, PFileLine, CommentLine, ControlLine, ValueLine
)


@PFileParser.register_type("dealIIPRM", "prm")
class PRMParser(PFileParser):
    @staticmethod
    def lines(fobj):
        def parse_command(cline, position):
            if not parse_line:
                return PFileLine()

            try:
                command, remainder = cline.split(' ', 1)
            except ValueError:
                command, remainder = cline, None

            try:
                if(command == 'subsection'):
                    remainder = remainder.strip()
                    position.append(remainder)
                    return ControlLine(command+' '+remainder, len(position)-1)
                elif(command == 'end'):
                    if(len(position) > 0):
                        position.pop()
                    else:
                        raise ValueError()
                    return ControlLine(command, len(position))
                elif(command == 'set'):
                    key, value = remainder.split('=', 1)
                    return ValueLine(':'.join(position+[key.strip()]),
                                     value.strip(),
                                     len(position))
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
                yield CommentLine(comment.strip())
                if not line.strip():
                    continue

            line = line.strip()

            if(line[-1:] == '\\'):
                parse_line += line[:-1].strip()+' '
                continue

            parse_line += line
            parse_line = parse_line.strip()

            yield parse_command(parse_line, position)

            parse_line = ""

        if parse_line:
            yield parse_command(parse_line, position)

        if len(position) > 0:
            raise ValueError("Did not exit subsection {}".format(
                ':'.join(position)))

    @staticmethod
    def typeset_line(line):
        if line.ltype == "Comment":
            return '# {}\n'.format(line.comment)
        elif line.ltype == "Control":
            return ('{ind:<{ind_s}}{line}\n'
                    .format(ind='',
                            ind_s=2*line.level,
                            line=line.line))
        elif line.ltype == "KeyValue":
            return ('{ind:<{indsp}}set {key} = {value}\n'
                    .format(ind='',
                            indsp=2*line.level,
                            key=line.key.rsplit(':', 1)[-1],
                            value=line.value))
        else:
            return '\n'
