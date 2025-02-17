#! python3
# coding: utf-8

from rdblns import readable_lines

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

# encode dat to lines
lns = readable_lines.encode(dat)

print(lns)

# decode lines to dat
dat2 = readable_lines.decode(lns)

assert dat == dat2
