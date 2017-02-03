import pytest
import copy
import sci_parameter_utils.parsers as parsers

full_parser_list = parsers.PFileParser._file_types.keys()
plist = copy.deepcopy(parsers.PFileParser._file_types)
# type: Dict[str, parsers.PFileParser]


class TrivialParser(parsers.PFileParser):
    @staticmethod
    def lines(pfile):
        linenum = 0
        for l in pfile:
            linenum += 1
            l = l.strip()
            if l == '':
                yield parsers.PFileLine.commentline(
                    None,
                    lnum=linenum)
            elif l.startswith('#'):
                yield parsers.PFileLine.commentline(
                    l[1:].strip(),
                    lnum=linenum)
            else:
                try:
                    key, value = l.split(' ', 1)
                except:
                    raise ValueError('Bad key-val on line {}: "{}"'
                                     .format(linenum, l))
                yield parsers.PFileLine.keyvalueline(
                    key, value,
                    lnum=linenum)

    @staticmethod
    def typeset_line(line):
        if line.ltype is None:
            return '\n'
        if line.ltype == "Comment":
            return "# {}\n".format(line.value)
        elif line.ltype == "KeyValue":
            return '{} {}'.format(line.key,
                                  line.value)
        else:
            raise ValueError("Unknown linetype: {}".format(str(line)))


plist['Trivial'] = TrivialParser  # type: ignore


@pytest.fixture(params=full_parser_list)
def parser(request):
    return plist[request.param]


@pytest.fixture
def param_file(request):
    with open(request.param, 'r') as f:
        yield f
