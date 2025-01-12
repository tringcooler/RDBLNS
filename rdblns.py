#! python3
# coding: utf-8

# MIT License
# 
# Copyright (c) 2025 Tring
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class c_readable_lines:

    SYM_BLNK = ''

    def _error_dec(self, ln, *txts):
        t = ' '.join((f'Dec(Ln {ln+1}):', *(str(v) for v in txts)))
        raise ValueError(t)

    def _error_enc(self, *txts):
        t = ' '.join((f'Enc:', *(str(v) for v in txts)))
        raise ValueError(t)

    def _decode(self, lines):
        stack = [{}]
        ckv = []
        elcnt = 0
        def _push_last():
            v, tli = ckv[-1]
            if len(ckv) == 1:
                self._error_dec(tli, 'invalid singular line:', v)
            cur = stack[-1]
            klen = len(ckv) - 1
            for i in range(klen):
                k, tli = ckv[i]
                if k in cur:
                    self._error_dec(tli, 'duplicated key:', k)
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
                        self._error_dec(li-1, 'too many pop ups:', elcnt)
                    elcnt -= 1
            ckv.append((line, li))
        if ckv:
            _push_last()
        return stack[0]

    def _enc_node(self, dat):
        vs = []
        sp = []
        deep = 0
        if not isinstance(dat, dict):
            vs.append(dat)
            return deep, vs, sp
        elif not dat:
            return None
        blank = self.SYM_BLNK
        for k, v in dat.items():
            if k == blank or v == blank:
                self._error_enc(f'empty line in dat {{{k}: {v}}}')
            nenc = self._enc_node(v)
            if nenc is None:
                continue
            if vs:
                assert deep > 0 and sp
                sp.append(deep)
            deep, nvs, nsp = nenc
            deep += 1
            vs.append(k)
            sp.append(0)
            vs.extend(nvs)
            sp.extend(nsp)
        if not vs:
            return None
        assert len(vs) == len(sp) + 1
        return deep, vs, sp

    def _encode(self, dat):
        blank = self.SYM_BLNK
        enc = self._enc_node(dat)
        if enc is None:
            return
        _, vs, sp = enc
        for i, (v, s) in enumerate(zip(vs, sp)):
            yield v
            for _ in range(s):
                yield blank
        yield vs[-1]

    @staticmethod
    def readlines(raw):
        if isinstance(raw, str):
            lines = raw.splitlines()
        elif callable(getattr(raw, 'readlines', None)):
            lines = raw.readlines()
        else:
            lines = raw
        return lines

    @staticmethod
    def writelines(lines, *, itr = False):
        if itr:
            return lines
        else:
            return '\n'.join(str(v) for v in lines)

    def decode(self, raw):
        return self._decode(self.readlines(raw))

    def encode(self, dat, **ka):
        return self.writelines(self._encode(dat), **ka)

readable_lines = c_readable_lines()

class lex_comment:

    SYM_CMT = '#'

    @staticmethod
    def readlines(raw):
        lines = c_readable_lines.readlines(raw)
        symcmt = lex_comment.SYM_CMT
        for line in lines:
            if line and isinstance(line, str):
                line = line.strip()
                if line[0] == symcmt:
                    continue
            yield line

    @staticmethod
    def writelines(lines, **ka):
        symcmt = lex_comment.SYM_CMT
        def _enc():
            for line in lines:
                if line and isinstance(line, tuple):
                    defer = []
                    for i, sline in enumerate(line):
                        if sline is None:
                            continue
                        if i > 0:
                            sline = symcmt + str(sline)
                        if i%2 == 0:
                            defer.append(sline)
                        else:
                            yield sline
                    yield from defer
                else:
                    yield line
        return c_readable_lines.writelines(_enc(), **ka)

if __name__ == '__main__':
    import pdb
    from pprint import pprint
    ppr = lambda *a, **ka: pprint(*a, **ka, sort_dicts = False)
    
    dat = {
        ('key 1', 'comment before key 1','comment after key 1', 'comment before key 1 again',  'comment after key 1 again', '...', '...'): {
            ('sub key 1', None, 'use None to bypass an unused comment'): ('sub val', 'value comments are the same'),
            'sub key 2': ('sub val 2', None, 'comments always follow their owners')
        },
        'key 2': 'val 2'
    }
    coder = c_readable_lines()

    lns = lex_comment.writelines(coder.encode(dat, itr=True))
    print(lns)

    dat2 = coder.decode(lex_comment.readlines(lns))
    ppr(dat2)
    
