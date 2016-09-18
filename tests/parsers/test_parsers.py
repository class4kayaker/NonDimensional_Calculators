import os.path
import glob
import pytest
import sci_parameter_utils.parsers as parsers


def list_files(dirn, fnglob):
    gl = os.path.join(dirn, fnglob)
    return glob.glob(gl)


def parser_dir(name):
    return os.path.join(os.path.dirname(__file__),
                        name)


@pytest.fixture
def param_file(request):
    with open(request.param, 'r') as f:
        yield f


@pytest.mark.parametrize(
    "parser,param_file",
    [(parsers.PRMParser, fn)
     for fn in list_files(parser_dir("dealIIPRM"), '*_rtrip.prm')],
    indirect=['param_file']
)
def test_parser_rtrip_rw(parser, param_file, tmpdir):
    testfile = tmpdir.join('out').open('w+')
    p = parser(param_file)
    for l in p.lines():
        testfile.write(p.typeset_line(l))
        testfile.write('\n')

    param_file.seek(0, 0)
    testfile.seek(0, 0)

    for l1, l2 in zip(param_file, testfile):
        assert l1 == l2


@pytest.mark.parametrize(
    "parser,param_file",
    [(parsers.PRMParser, fn)
     for fn in list_files(parser_dir("dealIIPRM"), '*_parse.prm')],
    indirect=['param_file']
)
def test_parser_parse(parser, param_file, tmpdir):
    p = parser(param_file)
    next_line = ''
    for l in p.lines():
        if l.ltype == "Comment":
            assert next_line == ''
            next_line = l.comment
        elif l.ltype is None:
            assert next_line == ''
        else:
            assert str(l) == next_line
            next_line = ''
