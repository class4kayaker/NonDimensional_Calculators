import re

repl_re = re.compile('{{{([^}]+)}}}')


def get_fn_suggest(tfile, parser):
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


def do_replace(istr, values, to_fmt=False):
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


def do_template(tfile, ofile, parser, values):
    tfile.seek(0, 0)
    for l in parser.lines(tfile):
        if l.ltype == 'KeyValue':
            l.value = do_replace(l.value,
                                 values)
            ofile.write(parser.typeset_line(l))
        else:
            ofile.write(parser.typeset_line(l))
