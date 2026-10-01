"""Create portable release assets without caches or local session data."""
from pathlib import Path
import hashlib,shutil,zipfile

root=Path(__file__).resolve().parents[1]
title='Damage Indicators for weapons'
output=root/'dist';output.mkdir(exist_ok=True)
executable=root/(title+'.exe')
if not executable.is_file():raise SystemExit('Build source/build.py first.')
shutil.copy2(executable,output/executable.name)
files=[root/name for name in ('README.md','LICENSE','CHANGELOG.md','requirements-build.txt')]
for folder in ('source','docs','licenses','tests','tools'):
 files.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo'))
with zipfile.ZipFile(output/(title+'.zip'),'w',zipfile.ZIP_DEFLATED) as archive:
 archive.write(executable,title+'/'+executable.name)
 for file in files:archive.write(file,title+'/'+file.relative_to(root).as_posix())
with zipfile.ZipFile(output/(title+'.zip')) as archive:
 if archive.testzip():raise SystemExit('Release ZIP verification failed.')
assets=[output/(title+'.exe'),output/(title+'.zip')]
(output/'SHA256.txt').write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name for p in assets)+'\n',encoding='utf-8')
print('Release assets ready in dist.')
