import re
import six
from sci_parameter_utils.parameter_file import PFileParser, KeyValuePair  # noqa: F401, E501
try:
    import typing  # noqa: F401
    from typing import Any, Pattern, Type  # noqa: F401
    from sci_parameter_utils.fragment import SearchElem  # noqa: F401
except:
    pass

repl_re = re.compile('{{{([^}]+)}}}')


def do_replace(istr, values, to_fmt=False, repl_re=repl_re):
    # type: (str, Dict[str, str], bool, Pattern) -> str
    def repl_fn(match):
        k = match.group(1)
        if to_fmt:
            return '{'+k+'}'
        else:
            if k not in values:
                raise ValueError(
                    "No element {} supplied".format(k))
            return values[k]
    return repl_re.sub(repl_fn, istr)


def get_fn_suggest(tfile, parser, repl_re=repl_re):
    # type: (typing.TextIO, Type[PFileParser], Pattern) -> str
    tfile.seek(0, 0)
    sugg_re = re.compile('FN:\s+(\S+)')
    lgen = parser.lines(tfile)
    for l in lgen:
        if l.ltype == "Comment":
            match = sugg_re.search(l.comment)
            if match:
                fn_suggest = match.group(1)
                break
    return do_replace(fn_suggest, None, to_fmt=True)


class ParserError(Exception):
    pass


def do_template(tfile, ofile, parser, values, repl_re=repl_re):
    # type: (typing.TextIO, typing.TextIO, Type[PFileParser], Dict[str, str], Pattern) -> None # noqa
    tfile.seek(0, 0)
    for l in parser.lines(tfile):
        if l.ltype == 'KeyValue':
            if isinstance(l.value, KeyValuePair):
                l.value.value = do_replace(l.value.value,
                                           values)
            else:
                raise ParserError(
                    "Key-value line does not have KeyValuePair value")
            ofile.write(six.text_type(parser.typeset_line(l)))
        else:
            ofile.write(six.text_type(parser.typeset_line(l)))


class MissingValues(Exception):
    pass


def do_search(searchlist, ifile, parser, findall=True):
    # type: (Dict[str, SearchElem], typing.TextIO, Type[PFileParser], bool) -> Dict[str, str] # noqa
    valdict = {}  # type: Dict[str, str]
    locdict = {}  # type: Dict[str, List[str]]
    for k in searchlist:
        lkey = searchlist[k].get_key()
        if lkey in locdict:
            locdict[lkey].append(k)
        else:
            locdict[lkey] = [k]

    for l in parser.lines(ifile):
        if l.ltype == "KeyValue":
            try:
                vlist = locdict[l.value.key]
            except KeyError:
                vlist = []

            for k in vlist:
                valdict[k] = searchlist[k].get_value(l.value.value)

    if findall:
        sset = set(searchlist.keys())
        vset = set(valdict.keys())
        if not sset == vset:
            raise MissingValues("Could not find values for {}"
                                .format(sset-vset))
    return valdict
