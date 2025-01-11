# RDBLNS

A data format with readable lines

## Description

- Describe dict data
- Use only blank lines to describe the format
- Use one line for each data item

## Example

source data:

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

to:

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

encode / decode by:

```python
from rdblns import c_readable_lines
coder = c_readable_lines()

# encode dat to lines
lns = coder.encode(dat)

print(lns)

# decode lines to dat
dat2 = coder.decode(lns)

assert dat == dat2
```