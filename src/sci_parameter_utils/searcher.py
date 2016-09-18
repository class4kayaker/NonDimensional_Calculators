class MissingValues(Exception):
    pass


def do_search(searchlist, ifile, parser, findall=True):
    valdict = {}
    locdict = {}
    for k in searchlist:
        lkey = searchlist[k].get_key()
        if lkey in locdict:
            locdict[lkey].append(k)
        else:
            locdict[lkey] = [k]

    for l in parser.lines(ifile):
        if l.ltype == "KeyValue":
            try:
                vlist = locdict[l.key]
            except KeyError:
                vlist = []

            for k in vlist:
                valdict[k] = searchlist[k].get_value(l.value)

    if findall:
        sset = set(searchlist.keys())
        vset = set(valdict.keys())
        if not sset == vset:
            raise MissingValues("Could not find values for {}"
                                .format(sset-vset))
    return valdict
