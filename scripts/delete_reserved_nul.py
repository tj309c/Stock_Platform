from pathlib import Path
import os

cwd = Path.cwd()
nul_path = cwd / 'nul'
print('Trying normal unlink...', nul_path.exists(), nul_path)
try:
    nul_path.unlink()
    print('Deleted nul using Path.unlink')
except Exception as e:
    print('Path.unlink failed:', e)
    # Try using extended path
    extended = r'\\?\\' + str(nul_path.absolute())
    try:
        os.remove(extended)
        print('Deleted nul using extended path')
    except Exception as e2:
        print('Extended remove failed:', e2)
        print('Try renaming as fallback...')
        try:
            fallback = cwd / 'nul-file-removed'
            os.rename(nul_path, fallback)
            print('Renamed to', fallback)
        except Exception as e3:
            print('Rename failed:', e3)

print('Done')
