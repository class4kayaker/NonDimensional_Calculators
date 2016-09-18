import pytest
import sci_parameter_utils.parameter_file as prm_file


@pytest.mark.parametrize("comment", [
    'Test 1',
    'Test 2',
])
def test_create_comment(comment):
    l = prm_file.CommentLine(comment)

    assert l.comment == comment


@pytest.mark.parametrize("line", [
    'Test 1',
    'Test 2',
])
@pytest.mark.parametrize("level", [
    1,
    2,
])
def test_create_control(line, level):
    l = prm_file.ControlLine(line, level)

    assert l.line == line
    assert l.level == level


@pytest.mark.parametrize("key", [
    'Test 1',
    'Test 2',
    'Test 3',
])
@pytest.mark.parametrize("value", [
    '3.4',
    '2.0',
    'True',
])
@pytest.mark.parametrize("level", [
    1,
    2,
])
def test_create_value(key, value, level):
    l = prm_file.ValueLine(key, value, level)

    assert l.key == key
    assert l.value == value
    assert l.level == level


class TPFileParser(prm_file.PFileParser):
    def __init__(self, fobj):
        pass  # pragma nocoverage

    def reset(self):
        pass  # pragma nocoverage

    def lines(self):
        pass  # pragma nocoverage

    def typeset_line(line):
        pass  # pragma nocoverage


@pytest.fixture
def create_mock_parser():
    def internal(name, extn):
        class Mock(TPFileParser):
            tdefn = name
            textn = extn
        return Mock
    return internal


@pytest.mark.parametrize("tstrs", [
    [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 1)],
    [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 2)],
])
def test_register_pfiles_parsers(tstrs, create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    for t, h in tstrs:
        prm_file.PFileParser.register_type(t, h)(
            create_mock_parser(t, h))

    for t, h in tstrs:
        obj = None
        e = prm_file.PFileParser.parser_by_name(t, obj)
        assert e.tdefn == t
        assert e.tdefn == t
        e = prm_file.PFileParser.parser_by_extn(h, obj)
        assert e.tdefn == t
        assert e.tdefn == t


@pytest.mark.parametrize("tstrs", [
    [('name'.format(i), 'extn{}'.format(i)) for i in range(0, 2)],
    [('name2'.format(i), 'extn{}'.format(i)) for i in range(0, 2)],
])
def test_register_pfiles_parser_collision(tstrs,
                                          create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    with pytest.raises(prm_file.ParserCollision) as excinfo:
        for t, h in tstrs:
            prm_file.PFileParser.register_type(t, h)(
                create_mock_parser(t, h))

    assert str(excinfo.value).startswith('Name ')
    assert str(excinfo.value).endswith(' is already registered')


@pytest.mark.parametrize("exc,error,fetch,tstrs", [
    (prm_file.ParserNotFound, 'No parser for nonex', 'nonex',
     [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 2)]),
    (prm_file.ParserNotFound, 'No parser for nonex', 'nonex',
     [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 3)]),
])
def test_fetch_name_pfiles_parsers(exc, error, fetch, tstrs,
                                   create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    for t, h in tstrs:
        prm_file.PFileParser.register_type(t, h)(
            create_mock_parser(t, h))

    with pytest.raises(exc) as excinfo:
        obj = None
        prm_file.PFileParser.parser_by_name(fetch, obj)

    if error:
        assert str(excinfo.value) == error


@pytest.mark.parametrize("exc,error,fetch,tstrs", [
    (prm_file.ParserNotFound, 'Extension nonex not known', 'nonex',
     [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 2)]),
    (prm_file.ParserNotFound, 'Extension extn ambiguous', 'extn',
     [('name{}'.format(i), 'extn'.format(i)) for i in range(0, 2)]),
])
def test_fetch_extn_pfiles_parsers(exc, error, fetch, tstrs,
                                   create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    for t, h in tstrs:
        prm_file.PFileParser.register_type(t, h)(
            create_mock_parser(t, h))

    with pytest.raises(exc) as excinfo:
        obj = None
        prm_file.PFileParser.parser_by_extn(fetch, obj)

    if error:
        assert str(excinfo.value) == error
