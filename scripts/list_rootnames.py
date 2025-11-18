import os
from pathlib import Path
p = Path.cwd()
for fname in sorted(os.listdir(p)):
    full = p / fname
    print(repr(fname), '->', 'dir' if full.is_dir() else 'file', 'size=', getattr(full.stat(), 'st_size', None))
