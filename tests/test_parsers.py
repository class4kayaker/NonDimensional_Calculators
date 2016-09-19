import os.path
import glob
import pytest
import sci_parameter_utils.parsers as parsers

full_parser_list = parsers.PFileParser._file_types.keys()


def list_files(dirn, fnglob):
    gl = os.path.join(dirn, fnglob)
    return glob.glob(gl)


def parser_dir(name):
    return os.path.join(os.path.dirname(__file__),
                        "parsers",
                        name)


@pytest.fixture
def param_file(request):
    with open(request.param, 'r') as f:
        yield f


def get_parser_tests(plist, endglob):
    olist = []
    for pn in plist:
        p = parsers.PFileParser.parser_by_name(pn)
        olist.extend(
            [(p, fn) for fn in
             list_files(parser_dir(pn), endglob)])
    return olist


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_parse.*'),
    indirect=['param_file']
)
def test_parser_parse(parser, param_file, tmpdir):
    next_line = ''
    for l in parser.lines(param_file):
        if l.ltype == "Comment":
            assert next_line == ''
            next_line = l.value
        elif l.ltype is None:
            assert next_line == ''
        else:
            assert str(l) == next_line
            next_line = ''


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_invalid.*'),
    indirect=['param_file']
)
def test_parser_parse_invalid(parser, param_file, tmpdir):
    lgen = parser.lines(param_file)
    fline = next(lgen)
    assert fline.ltype == "Comment"
    error = fline.value
    with pytest.raises(ValueError) as excinfo:
        for l in lgen:
            pass
    assert str(excinfo.value) == error


@pytest.mark.parametrize(
    "parser,line,out",
    [(parsers.PRMParser, l, o) for l, o in [
        (parsers.PFileLine('Comment', 'Test'), '# Test\n'),
        (parsers.PFileLine('Control', 'Test', level=1), '  Test\n'),
        (parsers.PFileLine('KeyValue', parsers.KeyValuePair('Test', 'Out'), 1),
         '  set Test = Out\n')
    ]]
)
def test_parser_typesetting(parser, line, out):
    l = parser.typeset_line(line)
    assert l == out


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_rtrip.*'),
    indirect=['param_file']
)
def test_parser_rtrip_rw(parser, param_file, tmpdir):
    fn1 = 'out'
    with tmpdir.join(fn1).open('w+') as testfile:
        for l in parser.lines(param_file):
            testfile.write(parser.typeset_line(l))

    del testfile

    param_file.seek(0, 0)
    with tmpdir.join(fn1).open('r') as testfile:
        for l1, l2 in zip(param_file, testfile):
            assert l1 == l2


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_rtrip.*'),
    indirect=['param_file']
)
def test_parser_rtrip_rw2(parser, param_file, tmpdir):
    fn1 = 'out'
    fn2 = 'out2'
    with tmpdir.join(fn1).open('w+') as testfile:
        for l in parser.lines(param_file):
            testfile.write(parser.typeset_line(l))

    with tmpdir.join(fn1).open('r') as testfile,\
            tmpdir.join(fn2).open('w+') as testfile2:
        for l in parser.lines(testfile):
            testfile2.write(parser.typeset_line(l))

    del testfile

    param_file.seek(0, 0)
    with tmpdir.join(fn1).open('r') as testfile,\
            tmpdir.join(fn2).open('r') as testfile2:
        for l1, l2, l3 in zip(param_file, testfile, testfile2):
            assert l1 == l2
            assert l2 == l3
