#! python3
# coding: utf-8

class c_readable_lines:

    SYM_CMT = '#'

    def _chk_nocmt(self, tok):
        if not (tok and isinstance(tok, str)):
            return 1
        symcmt = self.SYM_CMT
        if tok[0] == symcmt:
            if len(tok) > 1 and tok[1] == symcmt:
                return 2
            return 0
        return 1

    def _decode(self, lines):
        stack = [[]]
        elcnt = 0
        started = False
        for line in lines:
            line = line.strip()
            if not line:
                if started:
                    elcnt += 1
                continue
            cncmt = self._chk_nocmt(line)
            if cncmt == 2:
                line = line[1:]
            elif cncmt == 0:
                continue
            started = True
            cur = stack[-1]
            # prev shift. match with push. so even(more) for push
            if elcnt % 2 == 0:
                # even for push
                shft = elcnt // 2
                while shft > 0:
                    ncur = []
                    cur.append(ncur)
                    stack.append(ncur)
                    cur = ncur
                    shft -= 1
                cur.append(line)
            else:
                # odd for pop
                cur.append(line)
                shft = (elcnt + 1) // 2
                while shft > 0:
                    if len(stack) > 1:
                        stack.pop()
                        cur = stack[-1]
                    else:
                        assert len(stack) == 1
                        cur = [cur]
                        stack[0] = cur
                    shft -= 1
            elcnt = 0
        return stack[0]

    def _enc_deep(self, dat, deep):
        sp = []
        vs = []
        cmt = {}
        if not isinstance(dat, (list, tuple)):
            if self._chk_nocmt(dat) == 0:
                cmt[0] = [dat]
                return None, None, cmt
            else:
                return sp, [dat], cmt
        dlen = len(dat)
        if dlen == 0:
            return None, None, None
        # no need for reduce [[a, b]].
        #elif dlen == 1:
        #    return self._enc_deep(dat[0], deep)
        started = False
        for v in dat:
            ssp, svs, scmt = self._enc_deep(v, deep + 1)
            if scmt:
                for sci, scvs in scmt.items():
                    dci = sci + len(vs)
                    if not dci in cmt:
                        cmt[dci] = []
                    cmt[dci].extend(scvs)
            if svs is None:
                continue
            if started:
                sp.append(deep)
            else:
                started = True
            sp.extend(ssp)
            vs.extend(svs)
        vlen = len(vs)
        assert vlen == len(sp) + 1
        if vlen in cmt:
            # the last comment follow the prev.
            dci = vlen - 0.5
            if not dci in cmt:
                cmt[dci] = []
            cmt[dci].extend(cmt[vlen])
            del cmt[vlen]
        return sp, vs, cmt

    def _enc_posneg(self, v):
        # odd for neg, even for pos
        v *= 2
        if v < 0:
            v = - v - 1
        return v

    def _enc_diff(self, sp):
        slen = len(sp)
        if slen < 1:
            return
        lst = sp[0]
        for i in range(1, slen):
            ov = sp[i]
            diff = ov - lst
            sp[i-1] = self._enc_posneg(diff)
            lst = ov
        #diff = 0 - lst
        #sp[-1] = self._enc_posneg(diff)
        sp[-1] = 0 # no need for balance

    def _encode(self, dat):
        sp, vs, cmt = self._enc_deep(dat, 0)
        self._enc_diff(sp)
        r = []
        for i, (s, v) in enumerate(zip(sp, vs)):
            if i in cmt:
                for cv in cmt[i]:
                    r.append(cv)
            r.append(v)
            psti = i + 0.5
            if psti in cmt:
                for cv in cmt[psti]:
                    r.append(cv)
            for _ in range(s):
                r.append('')
        r.append(vs[-1])
        return r

    def decode(self, raw):
        if isinstance(raw, str):
            lines = raw.splitlines()
        elif callable(getattr(raw, 'readlines', None)):
            lines = raw.readlines()
        else:
            lines = raw
        return self._decode(lines)

    def encode(self, dat, itr = False):
        r = self._encode(dat)
        if itr:
            return r
        else:
            return '\n'.join(str(v) for v in r)
