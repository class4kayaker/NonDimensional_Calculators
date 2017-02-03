import pytest
import copy
import sci_parameter_utils.parameter_file as prm_file
import sci_parameter_utils.parsers as parsers

full_parser_list = parsers.PFileParser._file_types.keys()
plist = copy.deepcopy(parsers.PFileParser._file_types)


class TrivialParser(prm_file.PFileParser):
    @staticmethod
    def lines(pfile):
        linenum = 0
        for l in pfile:
            linenum += 1
            l = l.strip()
            if l == '':
                yield prm_file.PFileLine(None,
                                         None,
                                         lnum=linenum)
            elif l.startswith('#'):
                yield prm_file.PFileLine("Comment",
                                         l[1:].strip(),
                                         lnum=linenum)
            else:
                try:
                    key, value = l.split(' ', 1)
                except:
                    raise ValueError('Bad key-val on line {}: "{}"'
                                     .format(linenum, l))
                yield prm_file.PFileLine("KeyValue",
                                         prm_file.KeyValuePair(key, value),
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


plist['Trivial'] = TrivialParser


@pytest.fixture(params=full_parser_list)
def parser(request):
    return plist[request.param]


@pytest.fixture
def param_file(request):
    with open(request.param, 'r') as f:
        yield f
