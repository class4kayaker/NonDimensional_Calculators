from sci_parameter_utils.parameter_file import (
    PFileParser, PFileLine, CommentLine, ControlLine, ValueLine
)


@PFileParser.register_type("dealIIPRM", "prm")
class PRMParser(PFileParser):
    def __init__(self, fobj):
        self.fobj = fobj

    def reset(self):
        self.fobj.seek(0, 0)

    def lines(self):
        position = []
        parse_line = ""
        for line in self.fobj:
            # Strip comments
            if '#' in line:
                line, comment = line.split('#', 1)
                yield CommentLine(comment.strip())
                if not line.strip():
                    continue

            parse_line += line.strip()

            if(parse_line[-1:] == '\\'):
                continue

            if not parse_line:
                yield PFileLine()
                continue

            if(parse_line == 'end'):
                if(len(position) > 0):
                    position.pop()
                else:
                    raise ValueError("Invalid prm file")
                yield ControlLine(parse_line, len(position))
                parse_line = ""
                continue

            if ' ' in parse_line:
                command, remainder = parse_line.split(' ', 1)
            else:
                raise ValueError("Bad line: "+parse_line)

            parse_line = ""

            if(command == 'subsection'):
                remainder = remainder.strip()
                yield ControlLine(command+' '+remainder, len(position))
                position.append(remainder)
            elif(command == 'set'):
                key, value = remainder.split('=', 1)
                position.append(key.strip())
                yield ValueLine(':'.join(position), value.strip, len(position))
                position.pop()
            else:
                raise ValueError(
                    "Bad command {} with arg {}".format(command,
                                                        remainder))

    def typeset_line(self, line):
        if isinstance(line, CommentLine):
            return '# '+line.comment
        elif isinstance(line, ControlLine):
            return '  '*line.level+line.line
        elif isinstance(line, ValueLine):
            return '  '*line.level+'set '+line.key+' = '+line.value
        else:
            return ''
