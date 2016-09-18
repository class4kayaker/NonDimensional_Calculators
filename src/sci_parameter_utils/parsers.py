from sci_parameter_utils.parameter_file import (
    PFileParser, PFileLine, CommentLine, ControlLine, ValueLine
)


@PFileParser.register_type("dealIIPRM", "prm")
class PRMParser(PFileParser):
    @staticmethod
    def lines(fobj):
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

            if not parse_line:
                yield PFileLine()
                continue

            try:
                command, remainder = parse_line.split(' ', 1)
            except ValueError:
                command, remainder = parse_line, None

            parse_line = ""

            try:
                if(command == 'subsection'):
                    remainder = remainder.strip()
                    yield ControlLine(command+' '+remainder, len(position))
                    position.append(remainder)
                elif(command == 'end'):
                    if(len(position) > 0):
                        position.pop()
                    else:
                        raise ValueError()
                    yield ControlLine(command, len(position))
                elif(command == 'set'):
                    key, value = remainder.split('=', 1)
                    position.append(key.strip())
                    yield ValueLine(':'.join(position),
                                    value.strip(),
                                    len(position)-1)
                    position.pop()
                else:
                    raise ValueError()
            except ValueError:
                errstr = "Line {}: Bad command {}".format(linenum,
                                                          command)
                if remainder:
                    errstr.append(" with arg {}".format(remainder))
                raise ValueError(errstr)

        if len(position) > 0:
            raise ValueError("Did not exit subsection {}".format(
                ':'.join(position)))

    @staticmethod
    def typeset_line(line):
        if line.ltype == "Comment":
            return '# '+line.comment
        elif line.ltype == "Control":
            return '  '*line.level+line.line
        elif line.ltype == "KeyValue":
            return ('  '*line.level+'set ' +
                    line.key.rsplit(':', 1)[-1]+' = ' +
                    line.value)
        else:
            return ''
