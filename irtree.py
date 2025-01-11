#! python3
# coding: utf-8

import math
import itertools as itt

INF = float('inf')

class c_perm_idxs:

    def __init__(self):
        self.tab = [[[]], [[]]]

    def _calc(self, n):
        nv = n - 1
        for i in range(nv):
            for ps in self._iter(nv):
                rps = []
                hasnew = True
                for p in ps:
                    rp = []
                    for v in p:
                        rp.append(v)
                        if v == i:
                            assert hasnew
                            hasnew = False
                            rp.append(nv)
                    rps.append(rp)
                if hasnew:
                    rps.append([i, nv])
                yield rps
        yield from self._iter(nv)

    def _iter(self, n):
        tab = self.tab
        if n < len(tab):
            yield from tab[n]
            return
        rs = []
        for ps in self._calc(n):
            rs.append(ps)
            yield ps
        assert len(tab) == n
        tab.append(rs)

class c_irreducible_trees_tab:

    def __init__(self):
        self.tab = [0, 1]
        #self._permi = c_perm_idxs()

    def _x_dup_permutation(self, seq):
        for perms in self._permi._iter(len(seq)):
            r = list(seq)
            for pgrp in perms:
                wk = set()
                ph = pgrp[-1]
                for pi in pgrp:
                    v = seq[pi]
                    if v in wk:
                        break
                    wk.add(v)
                    r[ph] = v
                    ph = pi
                else:
                    continue
                break
            else:
                yield r, perms

    def _dup_permutation(self, seq):
        wk = set()
        for pseq in itt.permutations(seq):
            if pseq in wk:
                continue
            wk.add(pseq)
            yield pseq

    def _calc_grp(self, n, g, top = None):
        assert n >= g
        if g == 1:
            yield [n]
            return
        mn = math.ceil(n / g)
        mx = n - g + 1
        if not top is None:
            mx = min(mx, top)
        for i in range(mn, mx + 1):
            for sseq in self._calc_grp(n - i, g - 1, i):
                yield [i, *sseq]

    def _perm_grp(self, n, g):
        for seq in self._calc_grp(n, g):
            yield from self._dup_permutation(seq)

    def _do_prod(self, vs):
        return math.prod(vs)

    def _do_sum(self, v1, v2):
        return v1 + v2

    def _calc_val(self, n):
        vs = self._get_val(0)
        for g in range(2, n + 1):
            for seq in self._perm_grp(n, g):
                vp = self._do_prod(
                    self._get_val(ti)
                    for ti in seq)
                vs = self._do_sum(vs, vp)
        return vs

    def _get_val(self, n):
        tab = self.tab
        if n < len(tab):
            return tab[n]
        v = self._calc_val(n)
        assert n == len(tab)
        tab.append(v)
        return v

    def get(self, n):
        return self._get_val(n)

class c_irreducible_trees_tab_fast(c_irreducible_trees_tab):

    def __init__(self):
        super().__init__()
        self._cch_pn = [1]

    def _fast_perm_num(self, n):
        cch = self._cch_pn
        clen = len(cch)
        while n >= clen:
            cch.append(cch[-1] * clen)
            clen = len(cch)
        return cch[n]

    def _fast_dup_perm_num(self, seq):
        pnum = self._fast_perm_num(len(seq))
        lstn = 1
        lstv = None
        for v in seq:
            if v == lstv:
                lstn += 1
            else:
                pnum //= self._fast_perm_num(lstn)
                lstn = 1
                lstv = v
        pnum //= self._fast_perm_num(lstn)
        return pnum

    def _calc_val(self, n):
        vs = self._get_val(0)
        for g in range(2, n + 1):
            for seq in self._calc_grp(n, g):
                vp = self._do_prod(
                    self._get_val(ti)
                    for ti in seq)
                vp *= self._fast_dup_perm_num(seq)
                vs = self._do_sum(vs, vp)
        return vs

class c_irreducible_trees_tab_fast2(c_irreducible_trees_tab):

    def __init__(self):
        super().__init__()
        self._cch_gval = {}

    def _fast_calc_grp_val(self, n, g, top = INF):
        assert n >= g
        if g == 1:
            yield self._get_val(n), n, 1
            return
        key = (n, g)
        cch = self._cch_gval
        if key in cch:
            for (hd, hdcnt), val in cch[key].items():
                if not top is None and hd > top:
                    break
                yield val, hd, hdcnt
            return
        gcch = {}
        cch[key] = gcch
        mn = math.ceil(n / g)
        mx = min(n - g + 1, top)
        for i in range(mn, mx + 1):
            for val, hd, hdcnt in self._fast_calc_grp_val(n - i, g - 1, i):
                dval = self._get_val(i) * g * val
                if hd == i:
                    ncnt = hdcnt + 1
                    assert dval % ncnt == 0
                    dval //= ncnt
                else:
                    ncnt = 1
                gkey = (i, ncnt)
                if not gkey in gcch:
                    gcch[gkey] = 0
                gcch[gkey] += dval
                yield dval, i, ncnt

    def _calc_val(self, n):
        vs = self._get_val(0)
        for g in range(2, n + 1):
            vs += sum(
                val for val, hd, hdcnt in self._fast_calc_grp_val(n, g))
        return vs

class c_irreducible_trees_tab_detail(c_irreducible_trees_tab):

    def __init__(self):
        self.tab = [[], [1]]

    def _do_prod(self, vs):
        return list(
            list(pvs)
            for pvs in itt.product(*vs))

    def _do_sum(self, v1, v2):
        return v1 + v2

def calc_min_splitnum(mxn):
    ttab = c_irreducible_trees_tab_fast2()
    for i in range(2, mxn+1):
        v = ttab.get(i)
        msn = math.pow(v, 1/(i-1))
        print(f'{i} leaves {msn} split {v} trees')
    return ttab
