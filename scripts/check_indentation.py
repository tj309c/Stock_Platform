from pathlib import Path
p=Path('tests/unit/test_get_sec_rss_feeds.py')
text=p.read_text()
for i,line in enumerate(text.splitlines(), start=1):
    leading = len(line) - len(line.lstrip(' '))
    if leading != 0 and leading % 4 != 0:
        print('Line', i, 'leading spaces', leading, repr(line))
    if line.strip() == '':
        continue
print('Done')
