#! python3
# coding: utf-8

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
