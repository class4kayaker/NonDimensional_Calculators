import os.path
import glob
import pytest
import difflib
import six
import sci_parameter_utils.parsers as parsers
from io import StringIO

full_parser_list = parsers.PFileParser._file_types.keys()


@pytest.fixture
def parser(request):
    return parsers.PFileParser.parser_by_name(request.param)


@pytest.fixture
def param_file(request):
    with open(request.param, 'r') as f:
        yield f


def list_files(dirn, fnglob):
    gl = os.path.join(dirn, fnglob)
    return glob.glob(gl)


def parser_dir(name):
    return os.path.join(os.path.dirname(__file__),
                        "parsers",
                        name)


def get_parser_tests(plist, endglob):
    olist = []
    for pn in plist:
        olist.extend(
            [(pn, fn) for fn in
             list_files(parser_dir(pn), endglob)])
    return olist


def assert_nodiff_files(f1, f2, maxlen=50):
    diff = difflib.unified_diff(
        f1.readlines(),
        f2.readlines())

    diffl = ''
    n = maxlen
    for l in diff:
        if n <= 0:
            break
        n -= 1
        diffl += l
    if diffl:
        pytest.fail("Files differ: 1st 50 lines of diff:\n"+diffl)
    assert '' == diffl


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, 'parse_*.test'),
    indirect=True
)
def test_parser_parse(parser, param_file):
    ifile = StringIO()
    expect = StringIO()
    produce = StringIO()

    output = False
    for line in param_file.readlines():
        if line == "--{{{OUT}}}--\n":
            output = True
            continue
        if output:
            expect.write(six.text_type(line))
        else:
            ifile.write(six.text_type(line))
    ifile.seek(0)

    for line in parser.lines(ifile):
        produce.write(u"{!s}\n".format(line))

    assert expect.getvalue() == produce.getvalue()


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, 'invalid_*.test'),
    indirect=True
)
def test_parser_parse_invalid(parser, param_file, tmpdir):
    lgen = parser.lines(param_file)
    fline = next(lgen)
    assert fline.ltype == "Comment"
    error = fline.comment
    with pytest.raises(ValueError) as excinfo:
        for l in lgen:
            pass
    assert str(excinfo.value) == error


@pytest.mark.parametrize(
    "parser,line,out",
    [('dealIIPRM', l, o) for l, o in [
        (parsers.PFileLine.commentline('Test'), '# Test\n'),
        (parsers.PFileLine('Control', 'Test', level=1), '  Test\n'),
        (parsers.PFileLine.keyvalueline('Test', 'Out', 1),
         '  set Test = Out\n')
    ]],
    indirect=['parser']

)
def test_parser_typesetting(parser, line, out):
    l = parser.typeset_line(line)
    assert l == out


@pytest.mark.parametrize(
    "parser,line,error",
    [('dealIIPRM', l, o) for l, o in [
        (parsers.PFileLine('Unk', 'Test'), 'Unknown linetype: Unk'),
    ]],
    indirect=['parser']
)
def test_parser_typesetting_invalid(parser, line, error):
    with pytest.raises(ValueError) as excinfo:
        parser.typeset_line(line)
    assert str(excinfo.value) == error


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, 'rtrip_*.test'),
    indirect=True
)
def test_parser_rtrip_rw(parser, param_file, tmpdir):
    fexpect = StringIO(six.text_type(param_file.read()))
    fproduce = StringIO()

    param_file.seek(0, 0)
    for l in parser.lines(param_file):
        fproduce.write(six.text_type(parser.typeset_line(l)))

    assert fexpect.getvalue() == fproduce.getvalue()


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, 'rtrip_*.test'),
    indirect=True
)
def test_parser_rtrip_rw2(parser, param_file, tmpdir):
    fexpect = StringIO(six.text_type(param_file.read()))
    f1trip = StringIO()
    f2trip = StringIO()

    param_file.seek(0)
    for l in parser.lines(param_file):
        f1trip.write(six.text_type(parser.typeset_line(l)))

    f1trip.seek(0)
    for l in parser.lines(f1trip):
        f2trip.write(six.text_type(parser.typeset_line(l)))

    assert fexpect.getvalue() == f1trip.getvalue()
    assert fexpect.getvalue() == f2trip.getvalue()
