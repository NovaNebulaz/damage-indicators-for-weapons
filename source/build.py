"""Build the portable Windows launcher with PyInstaller 6.22.3."""
from pathlib import Path
from PyInstaller.__main__ import run

root=Path(__file__).resolve().parent
run([
 '--onefile','--windowed','--noconfirm','--noupx',
 '--name','Damage Indicators for weapons',
 '--distpath',str(root.parent),
 '--workpath',str(root.parent/'build'),
 '--specpath',str(root.parent/'build'),
 '--paths',str(root),
 '--add-data',str(root/'assets')+':assets',
 '--icon',str(root/'assets/launcher.ico'),
 '--version-file',str(root/'version.txt'),
 '--hidden-import','inventory_estimates',
 str(root/'launcher.py'),
])
