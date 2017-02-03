import pytest
import sci_parameter_utils.parameter_file as prm_file


@pytest.mark.parametrize("lnum", [
    1,
    4,
    5,
    10
])
@pytest.mark.parametrize("level", [
    0,
    3,
    2
])
@pytest.mark.parametrize(
    "ltype,value",
    [("Comment", "Test {}".format(i)) for i in range(3, 5)] +
    [("Control", "Test {}".format(i)) for i in range(2, 4)] +
    [("KeyValue", str(prm_file.KeyValuePair("K", "Test {}".format(i))))
     for i in range(4, 6)]
)
def test_create_fline(ltype, lnum, level, value):
    a = prm_file.PFileLine(ltype, value, level, lnum)

    assert a.ltype == ltype
    assert a.value == value
    assert a.level == level
    assert a.lnum == lnum
    assert str(a) == ("<{} [Line {}]({}): {}>"
                      .format(a.ltype,
                              a.lnum,
                              a.level,
                              str(a.value)))


@pytest.mark.parametrize("lnum", [
    1,
    4,
    5,
    10
])
@pytest.mark.parametrize("value", [
    "Val 1"
    "Val 2"
])
def test_create_fline_c(value, lnum):
    a = prm_file.PFileLine.commentline(value,
                                       lnum=lnum)

    assert a.ltype == "Comment"
    assert a.value == value
    assert a.lnum == lnum
    assert str(a) == ("<{} [Line {}]({}): {}>"
                      .format(a.ltype,
                              lnum,
                              0,
                              value))


@pytest.mark.parametrize("lnum", [
    1,
    4,
    5,
    10
])
@pytest.mark.parametrize("level", [
    0,
    3,
    2
])
@pytest.mark.parametrize("key", [
    "Key 1"
    "Key 2"
])
@pytest.mark.parametrize("value", [
    "Val 1"
    "Val 2"
])
def test_create_fline_kv(key, value, level, lnum):
    a = prm_file.PFileLine.keyvalueline(key,
                                        value,
                                        level,
                                        lnum)

    assert a.ltype == "KeyValue"
    assert a.value.key == key
    assert a.value.value == value
    assert a.level == level
    assert a.lnum == lnum
    assert str(a) == ("<{} [Line {}]({}): <{} = {}>>"
                      .format(a.ltype,
                              lnum,
                              level,
                              key,
                              value))


@pytest.fixture
def create_mock_parser():
    def internal(name, extn):
        class Mock(prm_file.PFileParser):
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
        c = create_mock_parser(t, h)
        co = prm_file.PFileParser.register_type(t, h)(c)
        assert c == co

    for t, h in tstrs:
        e = prm_file.PFileParser.parser_by_name(t)
        assert e.tdefn == t
        assert e.tdefn == t
        e = prm_file.PFileParser.parser_by_extn(h)
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
def test_fetch_name_pfiles_parsers_err(exc, error, fetch, tstrs,
                                       create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    for t, h in tstrs:
        prm_file.PFileParser.register_type(t, h)(
            create_mock_parser(t, h))

    with pytest.raises(exc) as excinfo:
        prm_file.PFileParser.parser_by_name(fetch)

    if error:
        assert str(excinfo.value) == error


@pytest.mark.parametrize("exc,error,fetch,tstrs", [
    (prm_file.ParserNotFound, 'Extension nonex not known', 'nonex',
     [('name{}'.format(i), 'extn{}'.format(i)) for i in range(0, 2)]),
    (prm_file.ParserNotFound, 'Extension extn ambiguous', 'extn',
     [('name{}'.format(i), 'extn'.format(i)) for i in range(0, 2)]),
])
def test_fetch_extn_pfiles_parsers_err(exc, error, fetch, tstrs,
                                       create_mock_parser, monkeypatch):
    test_types = {}
    test_extns = {}
    monkeypatch.setattr(prm_file.PFileParser, '_file_types', test_types)
    monkeypatch.setattr(prm_file.PFileParser, '_file_extns', test_extns)

    for t, h in tstrs:
        prm_file.PFileParser.register_type(t, h)(
            create_mock_parser(t, h))

    with pytest.raises(exc) as excinfo:
        prm_file.PFileParser.parser_by_extn(fetch)

    if error:
        assert str(excinfo.value) == error
