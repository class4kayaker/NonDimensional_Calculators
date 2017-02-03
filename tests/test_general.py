import pytest
import sci_parameter_utils.general as gen
import sci_parameter_utils.parameter_file as prm_file
import sci_parameter_utils.fragment as frags
from io import StringIO
import six


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


@pytest.mark.parametrize("key", [
    "Key1",
    "Key2"
])
@pytest.mark.parametrize("name", [
    'a',
])
@pytest.mark.parametrize("value", [
    ('Hello', str),
    (1, int),
    (1.0, float),
])
def test_fn_template_basic(parser, tmpdir, key, name, value):
    lt = prm_file.PFileLine.keyvalueline(key, '{{{'+name+'}}}')
    lo = prm_file.PFileLine.keyvalueline(key, value)
    smap = {name: '{}'.format(value)}
    f_t = StringIO(six.text_type(parser.typeset_line(lt)))
    f_o = StringIO(six.text_type(parser.typeset_line(lo)))
    f_g = StringIO()
    try:
        gen.do_template(f_t, f_g, parser, smap)
        assert f_g.getvalue() == f_o.getvalue()
    finally:
        f_t.close()
        f_o.close()
        f_g.close()


@pytest.mark.parametrize("key", [
    "Key1",
    "Key2"
])
@pytest.mark.parametrize("value,vf", [
    ('Hello', str),
    (1, int),
    (1.0, float),
])
def test_fn_search_basic(parser, tmpdir, key, value, vf):
    fn = 'out'
    n = 'Name'
    smap = {n: frags.LocElem(n, key)}
    l = prm_file.PFileLine.keyvalueline(key, value)
    tmpdir.join(fn).write(parser.typeset_line(l))

    with tmpdir.join(fn).open('r') as f:
        out = gen.do_search(smap, f, parser)
        assert value == vf(out[n])
