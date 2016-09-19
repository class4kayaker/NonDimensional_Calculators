import pytest
import sci_parameter_utils.general as gen
import sci_parameter_utils.parameter_file as prm_file


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
            if l.startswith('#'):
                yield prm_file.PFileLine("Comment",
                                         l[1:].strip(),
                                         lnum=linenum)
            else:
                try:
                    key, value = l.split(' ', 1)
                except:
                    raise ValueError('Bad key-val on line {}: {}'
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


@pytest.mark.parametrize("istr,values,ostr", [
    ("", {}, ""),
    ("", {'a': 'b'}, ""),
    ("{{{a}}}", {'a': 'b'}, "b"),
    ("{{{a}}}{{{a}}}", {'a': 'b'}, "bb"),
    ("{{{c}}}{{{a}}}", {'a': 'b', 'c': 'd'}, "db"),
])
def test_replace(istr, values, ostr):
    assert ostr == gen.do_replace(istr, values)


@pytest.mark.parametrize("istr,values,ostr", [
    ("", {}, ""),
    ("", {'a': 'b'}, ""),
    ("{{{a}}}{{{a}}}", {'a': 'b'}, "{a}{a}"),
    ("{{{c}}}{{{a}}}", {'a': 'b', 'c': 'd'}, "{c}{a}"),
])
def test_replace_tofmt(istr, values, ostr):
    assert ostr == gen.do_replace(istr, values, to_fmt=True)
