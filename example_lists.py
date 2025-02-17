#! python3
# coding: utf-8

from rdblns import readable_lines, trans_lines

dat = [{
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

# encode dat to lines
lns = readable_lines.writelines(
    trans_lines(
        trans_lines(
            readable_lines.encode(list2dict(dat), itr=True),
            trim_listkey_1,
        ),
        trim_listkey_2,
    )
)

print(lns)

# decode lines to dat
dat2 = dict2list(readable_lines.decode(
    trans_lines(
        readable_lines.readlines(lns),
        make_expand_listkey(),
    )
))

assert dat == dat2
