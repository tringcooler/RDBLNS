# RDBLNS

A data format with readable lines

## Description

- Describe dict data
- Use only blank lines to describe the format
- Use one line for each data item

## Example

### Basic

Source data:

```python
dat = {
    'key 1 in root': 'value for key 1',
    'key 2 in root': 'value for key 2',
    'key for sub dict': {
        'key 1 in sub': {
            'keys in streak lines': 'then values in the last',
        },
        'blank lines before keys mean to pop up': {
            'keys begin from the most common parent': 'values always in the last'
        }
    },
    'the number of blank lines popping up': 'No need for blank line balancing after the last value'
}
```

Encode / Decode by:

```python
from rdblns import readable_lines

# encode dat to lines
lns = readable_lines.encode(dat)

print(lns)

# decode lines to dat
dat2 = readable_lines.decode(lns)

assert dat == dat2
```

Result lines:

```
key 1 in root
value for key 1

key 2 in root
value for key 2

key for sub dict
key 1 in sub
keys in streak lines
then values in the last


blank lines before keys mean to pop up
keys begin from the most common parent
values always in the last



the number of blank lines popping up
No need for blank line balancing after the last value
```

### Custom

#### Comments Syntax

The output lines can be customized by "breakable_lines" function

A example of adding comments:

``` python
from rdblns import readable_lines, breakable_lines

# Customize a breakable encoder
def brk_encode():

    # The symbol for break
    brk = object()
    
    for bi, lines in enumerate(breakable_lines(readable_lines.encode(
    
            # The most outside dict
            {
                # the 1st break point here
                'dest key 1': brk,
                
                'dest key 2': {
                    # the 2nd break point here
                    'dest sub key': brk,
                },
                
                # the 3rd break point here, at a key
                brk: 'break key value',
                
                'another key': 'some values'
            },
            
            itr = True), brk)):
        yield from lines
        if bi == 0:
            # At the 1st break point
            
            yield '# comment before sub key 1'
            # Insert a new dict
            yield from readable_lines.encode({
                'sub key 1': 'sub val 1'
            }, itr = True, inner = True)
            
            yield '# comment before sub key 2'
            yield from readable_lines.encode({
                'sub key 2': {'sub sub key': 'sub val 2'}
            }, itr = True, inner = True)
            yield '# comment after sub 2'
            
        elif bi == 1:
            # At the 2nd break point
            
            yield '# comment before the value'
            yield from readable_lines.encode(
                'just a value', itr = True, inner = True)
            yield '# comment after the value'
            
        elif bi == 2:
            # At the 3rd break point
            
            yield '# comment before the key'
            yield from readable_lines.encode(
                'just a key', itr = True, inner = True)
            yield '# comment after the key'

# Custom a commented lines reader
def comment_readlines(raw):
    
    # read lines by original reader
    lines = readable_lines.readlines(raw)
    
    symcmt = '#'
    for line in lines:
        if isinstance(line, str):
            line = line.strip()
            if line and line[0] == symcmt:
                # Just bypass comments
                continue
        yield line

# Encode by custom encoder, and write by orignal writer
lns = readable_lines.writelines(brk_encode())
print(lns)

# Decode by orignal decoder, and read by custom reader
dat = readable_lines.decode(comment_readlines(lns))
from pprint import pprint
pprint(dat, sort_dicts = False)
```

Result lines:

```
dest key 1
# comment before sub key 1
sub key 1
sub val 1

# comment before sub key 2
sub key 2
sub sub key
sub val 2


# comment after sub 2

dest key 2
dest sub key
# comment before the value
just a value
# comment after the value


# comment before the key
just a key
# comment after the key
break key value

another key
some values
```

Result decoded data:

```python
{'dest key 1': {'sub key 1': 'sub val 1',
                'sub key 2': {'sub sub key': 'sub val 2'}},
 'dest key 2': {'dest sub key': 'just a value'},
 'just a key': 'break key value',
 'another key': 'some values'}
```

#### Lists Syntax

The output lines can be customized by "trans_lines" function

A example of adding lists supporting:

``` python
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
```

Result lines:

```
:
a value
value 1

this is a list:
the meber
can be a dict

as normal
recursived
value r

,
or a value,:
or,
another,
list
,:::
and,
or
,
more
,::
recursived
,
lists




this is a dict
a list inside the dict:
la,
lb,
lc


,
etc
```
