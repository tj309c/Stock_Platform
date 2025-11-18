from pathlib import Path
p=Path('tests/unit/test_get_sec_rss_feeds.py')
text=p.read_text(encoding='utf8')
lines=text.splitlines()
print('Lines:', len(lines))
print('\nHeader:\n', '\n'.join(lines[:20]))
print('\nTail:\n', '\n'.join(lines[-20:]))
