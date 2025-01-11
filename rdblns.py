#! python3
# coding: utf-8

class c_readable_lines:

    SYM_BLNK = ''

    def _error(self, ln, *txts):
        t = ' '.join((f'Ln {ln+1}:', *(str(v) for v in txts)))
        raise ValueError(t)

    def _decode(self, lines):
        stack = [{}]
        ckv = []
        elcnt = 0
        def _push_last():
            v, tli = ckv[-1]
            if len(ckv) == 1:
                self._error(tli, 'invalid singular line:', v)
            cur = stack[-1]
            klen = len(ckv) - 1
            for i in range(klen):
                k, tli = ckv[i]
                if k in cur:
                    self._error(tli, 'duplicated key:', k)
                if i == klen - 1:
                    cur[k] = v
                else:
                    cur[k] = {}
                    cur = cur[k]
                    stack.append(cur)
        started = False
        for li, line in enumerate(lines):
            line = line.strip()
            if not line:
                if started:
                    elcnt += 1
                continue
            started = True
            if elcnt > 0:
                # push last
                assert ckv
                _push_last()
                ckv.clear()
                # pop
                elcnt -= 1
                while elcnt > 0:
                    stack.pop()
                    if not stack:
                        self._error(li-1, 'too many pop ups:', elcnt)
                    elcnt -= 1
            ckv.append((line, li))
        if ckv:
            _push_last()
        return stack[0]

    def _enc_node(self, dat):
        assert dat
        vs = []
        sp = []
        deep = 0
        if not isinstance(dat, dict):
            vs.append(dat)
            return deep, vs, sp
        blank = self.SYM_BLNK
        for k, v in dat.items():
            if k == blank or v == blank:
                raise ValueError(f'empty line in dat {{{k}: {v}}}')
            elif not v:
                continue
            if vs:
                assert deep > 0 and sp
                sp.append(deep)
            deep, nvs, nsp = self._enc_node(v)
            deep += 1
            vs.append(k)
            sp.append(0)
            vs.extend(nvs)
            sp.extend(nsp)
        assert len(vs) == len(sp) + 1
        return deep, vs, sp

    def _encode(self, dat):
        if not dat:
            return
        blank = self.SYM_BLNK
        _, vs, sp = self._enc_node(dat)
        for i, (v, s) in enumerate(zip(vs, sp)):
            yield v
            psti = i + 0.5
            for _ in range(s):
                yield blank
        yield vs[-1]

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
