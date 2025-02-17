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

    def _encode(self, dat, inner = False, **ka):
        blank = self.SYM_BLNK
        enc = self._enc_node(dat)
        if enc is None:
            return
        deep, vs, sp = enc
        for i, (v, s) in enumerate(zip(vs, sp)):
            yield v
            for _ in range(s):
                yield blank
        yield vs[-1]
        if inner:
            for _ in range(deep):
                yield blank

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
    def writelines(lines, *, itr = False, **ka):
        if itr:
            return lines
        else:
            return '\n'.join(str(v) for v in lines)

    def decode(self, raw):
        return self._decode(self.readlines(raw))

    def encode(self, dat, **ka):
        return self.writelines(self._encode(dat, **ka), **ka)

readable_lines = c_readable_lines()

def breakable_lines(lines, brk):
    itr = iter(lines)
    cbbrk = callable(brk)
    def _itr_lines(la):
        yield la
        for line in itr:
            if (cbbrk and brk(line)) or line is brk:
                return line
            yield line
        return None
    while True:
        try:
            lookahead = next(itr)
        except StopIteration:
            break
        yield _itr_lines(lookahead)

def trans_lines(lines, cb_trans_itr, EOLS= None):
    itr = iter(lines)
    cch = []
    transed = []
    def _itr_cch():
        while True:
            cch_idx = 0
            while not transed:
                src_done = False
                while cch_idx >= len(cch):
                    try:
                        line = next(itr)
                    except StopIteration:
                        src_done = True
                        break
                    cch.append(line)
                if src_done:
                    yield EOLS
                    continue
                yield cch[cch_idx]
                cch_idx += 1
            assert not transed[0] is None or len(transed) == 1
            if not transed[0] is None:
                for _ in range(cch_idx):
                    # drop transed lines
                    if not cch:
                        break
                    cch.pop(0)
                for tline in reversed(transed):
                    cch.insert(0, tline)
            transed.clear()
    citr = _itr_cch()
    while True:
        for tline in cb_trans_itr(citr):
            transed.append(tline)
        if not transed:
            if cch:
                yield cch.pop(0)
                transed.append(None)
            else:
                break

if __name__ == '__main__':
    from pprint import pprint
    ppr = lambda *a: pprint(*a, sort_dicts=False)

    src = [{
        'a value': 'value 1',
        'this is a list': [
            {
                'the meber': 'can be a dict',
                'as normal': {'recursived': 'value r'},
            },
            'or a value',
            ['or', 'another', 'list'],
            [[['and', 'or'], 'more'], [['recursived'], 'lists']],
        ],
        'this is a dict': {
            'a list inside the dict': ['la', 'lb', 'lc']
        },
    }, 'etc']

    def list2dict(src):
        if isinstance(src, dict):
            itr = src.items()
        elif isinstance(src, list):
            itr = ((f'__{i}', v) for i, v in enumerate(src))
        else:
            return src
        r = {}
        for k, v in itr:
            r[k] = list2dict(v)
        return r

    def dict2list(src):
        if not isinstance(src, dict):
            return src
        rs = None
        for k, v in src.items():
            v = dict2list(v)
            if k.startswith('__') and k[2:].isdigit():
                if rs is None:
                    rs = []
                rs.append(v)
            else:
                if rs is None:
                    rs = {}
                rs[k] = v
        return rs

    def trim_listkey_1(itr):
        bline = next(itr)
        if bline == '__0':
            yield '__:'
            return
        cline = next(itr)
        if not cline or not cline.startswith('__'):
            return
        cv = cline[2:]
        if not cv.isdigit():
            return
        cv = int(cv)
        if cv == 0:
            return
        yield bline + '__,'

    def trim_listkey_2(itr):
        symsplits = ('__:', '__,')
        bline = next(itr)
        if bline in symsplits:
            yield bline[2:]
            return
        cline = next(itr)
        if not cline in symsplits:
            return
        yield bline + cline[2:]

    def make_expand_listkey():
        kidx = [0]
        def expand_listkey(itr):
            line = next(itr)
            if line is None:
                return
            llen = len(line)
            rs = []
            for i, c in enumerate(reversed(line)):
                listkey = f'__{kidx[0]}'
                if c == ':':
                    rs.append(listkey)
                elif c == ',':
                    rs.append(listkey)
                    rs.append('')
                else:
                    rs.append(line[:llen - i])
                    break
                kidx[0] += 1
            else:
                rs.append('')
            if len(rs) > 1:
                for rline in reversed(rs):
                    yield rline
        return expand_listkey

    ppr(list2dict(src))
    #print('===')
    #print(readable_lines.encode(list2dict(src)))
    print('===')
    rlines = readable_lines.writelines(
        trans_lines(
            trans_lines(
                readable_lines.encode(list2dict(src), itr=True),
                trim_listkey_1,
            ),
            trim_listkey_2,
        )
    )
    print(rlines)
    print('===')
    dat = dict2list(readable_lines.decode(
        trans_lines(
            readable_lines.readlines(rlines),
            make_expand_listkey(),
        )
    ))
    assert src == dat
    ppr(dat)
