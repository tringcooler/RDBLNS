# RDBLNS

A data format with readable lines

## Description

- Describe dict data
- Use only blank lines to describe the format
- Use one line for each data item

## Example

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

## Custom

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
        if line and isinstance(line, str):
            line = line.strip()
            if line[0] == symcmt:
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
