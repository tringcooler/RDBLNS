#! python3
# coding: utf-8

from irtree import c_irreducible_trees_tab_detail

def the_most_simplest_encode(arrtree, deep = 0):
    r = []
    if not isinstance(arrtree, list):
        return r
    for i, v in enumerate(arrtree):
        if i > 0:
            r.append(deep)
        r.extend(the_most_simplest_encode(v, deep + 1))
    return r

def trimed_tms_encode(arrtree):
    seq = the_most_simplest_encode(arrtree)
    slen = len(seq)
    if slen < 1:
        return seq
    lst = seq[0]
    seq[0] = 0
    for i in range(1, slen):
        ov = seq[i]
        nv = ov - lst
        seq[i] = nv
        lst = ov
    return seq

def kv2_arr_modifier(arrtree):
    if not isinstance(arrtree, list):
        return arrtree
    r = []
    for v in arrtree:
        kv2 = [0]
        kv2.append(kv2_arr_modifier(v))
        r.append(kv2)
    return r

def kv2_arr_encode(arrtree):
    seq = trimed_tms_encode(arrtree)
    return [
        -v if v < 0 else 0
        for v in seq]

def str_modifier(arrtree):
    if not isinstance(arrtree, list):
        return str(arrtree)
    r = []
    for v in arrtree:
        r.append(str_modifier(v))
    return r

def kv2_dict_modifier(arrtree):
    if not isinstance(arrtree, list):
        return str(arrtree)
    r = {}
    for i, v in enumerate(arrtree):
        key = f'k{i}'
        r[key] = kv2_dict_modifier(v)
    return r

def check_irtrees(mxn, enc, dec = None, mod = None, verb = 0):
    ttab = c_irreducible_trees_tab_detail()
    rvs = {}
    for i in range(2, mxn+1):
        print(f'check {i} leaves ... ', end = None if verb else '')
        for j, arrtree in enumerate(ttab.get(i)):
            if callable(mod):
                arrtree = mod(arrtree)
            encval = enc(arrtree)
            if isinstance(encval, list):
                encval = tuple(encval)
            if verb:
                vnxt = (verb > 1)
                print(f'{j}: {encval}', end = '' if vnxt else None)
                if vnxt:
                    print(arrtree)
            if encval in rvs:
                raise ValueError(f'dup encoded value: {encval}')
            rvs[encval] = (i, j)
            if callable(dec):
                decval = dec(encval)
                if not decval == arrtree:
                    raise ValueError(f'unmatch: {arrtree} / {decval}')
        print('done')
    return rvs

if __name__ == '__main__':
    import pdb
    from pprint import pprint
    ppr = lambda *a, **ka: pprint(*a, **ka, sort_dicts = False)

    def test_base(mxn):
        check_irtrees(mxn, verb = 0,
            enc = the_most_simplest_encode)
        check_irtrees(mxn, verb = 0,
            enc = trimed_tms_encode)
        check_irtrees(mxn, verb = 0,
            enc = kv2_arr_encode,
            mod = kv2_arr_modifier)

    from rdblns_legacy import c_readable_lines as c_rdblns_lgcy
    from rdblns import c_readable_lines as c_rdblns

    def test_rdblns(mxn):
        encoder = c_rdblns_lgcy()
        check_irtrees(mxn, verb = 0,
            enc = encoder.encode,
            dec = encoder.decode,
            mod = str_modifier)
        encoder = c_rdblns()
        check_irtrees(mxn, verb = 0,
            enc = encoder.encode,
            dec = encoder.decode,
            mod = kv2_dict_modifier)
    
    test_rdblns(10)
