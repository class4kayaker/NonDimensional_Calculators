import os.path
import glob
import pytest
import difflib
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
        print(diffl)
        assert False
    else:
        assert '' == diffl


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_parse.*'),
    indirect=['param_file']
)
def test_parser_parse(parser, param_file, tmpdir):
    cfn = 'out-c'
    pfn = 'out-p'
    with tmpdir.join(cfn).open('w') as cf, \
            tmpdir.join(pfn).open('w') as pf:
        for l in parser.lines(param_file):
            cfmt = '# {}\n'
            pfmt = '# L: {}\n'
            if l.ltype == "Comment":
                if l.value.startswith('L: '):
                    cf.write(cfmt.format(l.value))
                else:
                    pf.write(pfmt.format(str(l)))
            else:
                pf.write(pfmt.format(str(l)))

    with tmpdir.join(cfn).open('r') as cf, \
            tmpdir.join(pfn).open('r') as pf:
        assert_nodiff_files(cf, pf)


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
    param_file.seek(0, 0)
    with tmpdir.join(fn1).open('w') as testfile:
        for l in parser.lines(param_file):
            testfile.write(parser.typeset_line(l))

    del testfile

    param_file.seek(0, 0)
    with tmpdir.join(fn1).open('r') as testfile:
        diff = ''.join(difflib.unified_diff(
            param_file.readlines(),
            testfile.readlines()))
        assert '' == diff


@pytest.mark.parametrize(
    "parser,param_file",
    get_parser_tests(full_parser_list, '*_rtrip.*'),
    indirect=['param_file']
)
def test_parser_rtrip_rw2(parser, param_file, tmpdir):
    fn1 = 'out'
    fn2 = 'out2'
    with tmpdir.join(fn1).open('w') as testfile:
        for l in parser.lines(param_file):
            testfile.write(parser.typeset_line(l))

    with tmpdir.join(fn1).open('r') as testfile,\
            tmpdir.join(fn2).open('w') as testfile2:
        for l in parser.lines(testfile):
            testfile2.write(parser.typeset_line(l))

    del testfile

    param_file.seek(0, 0)
    with tmpdir.join(fn1).open('r') as testfile:
        assert_nodiff_files(param_file, testfile)

    del testfile

    param_file.seek(0, 0)
    with tmpdir.join(fn2).open('r') as testfile:
        assert_nodiff_files(param_file, testfile)
