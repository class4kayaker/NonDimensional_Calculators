import pytest
import sci_parameter_utils.general as gen
import sci_parameter_utils.parameter_file as prm_file


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


@pytest.mark.parametrize("istr,values,error", [
    ("{{{a}}}", {'b': 'b'}, "No element a supplied"),
    ("{{{a}}}{{{a}}}", {'b': 'b'}, "No element a supplied"),
    ("{{{c}}}{{{a}}}", {'d': 'b', 'c': 'd'}, "No element a supplied"),
])
def test_replace_invalid(istr, values, error):
    with pytest.raises(ValueError) as excinfo:
        gen.do_replace(istr, values)
    assert str(excinfo.value) == error


@pytest.mark.par
@pytest.mark.parametrize('sugg,ostr', [
    ('out', 'out'),
    ('test', 'test'),
    ('{{{a}}}', '{a}'),
])
def test_fn_suggest_basic(parser, tmpdir, sugg, ostr):
    fn = 'out'
    l = prm_file.PFileLine.commentline("FN: {}".format(sugg))
    tmpdir.join(fn).write(parser.typeset_line(l))

    with tmpdir.join(fn).open('r') as f:
        assert ostr == gen.get_fn_suggest(f, parser)
