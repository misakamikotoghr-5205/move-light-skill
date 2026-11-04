"""Build a portable Skill ZIP; excludes tests, runtime data, and repository metadata."""
from pathlib import Path
import zipfile
root = Path(__file__).resolve().parent.parent
source = root / 'skill/move-light'
output = root / 'submission/move-light.zip'
output.parent.mkdir(exist_ok=True)
files = sorted(path for path in source.rglob('*') if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for file in files:
        info = zipfile.ZipInfo(str(file.relative_to(source)), date_time=(2026, 11, 4, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, file.read_bytes())
print(f'{output}: {len(files)} files, {output.stat().st_size} bytes')
