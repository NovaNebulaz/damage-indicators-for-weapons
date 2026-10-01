"""Steam discovery and reversible installation for Damage Indicators for weapons."""
from __future__ import annotations
import hashlib,json,os,pathlib,re,shutil,subprocess,sys,time,uuid,winreg

TITLE='Damage Indicators for weapons'
APP_ID='1912410'
EXPECTED='7c83afbf0ad34a40b853cdb25a22fffb605d08e2a1e2d431974d7c7c1ee0ba54'
ROOT=pathlib.Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
STATE=pathlib.Path(os.environ.get('LOCALAPPDATA',str(pathlib.Path.home()/'AppData/Local')))/'DamageIndicatorsForWeapons'
STEM='zzz_DamageIndicatorsForWeapons_P'
EXTENSIONS=('pak','ucas','utoc')
EXE=pathlib.Path('Dungeons/Binaries/Win64/Dungeons-Win64-Shipping.exe')

def digest(path):
 with pathlib.Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def atomic_json(path,data):
 path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
 try:
  temporary.write_text(json.dumps(data,indent=2),encoding='utf-8');temporary.replace(path)
 finally:temporary.unlink(missing_ok=True)

def vdf(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|\{|\}|[^\s{}"]+',re.sub(r'//[^\r\n]*','',text))
 def value(token):return re.sub(r'\\([\\"])',r'\1',token[1:-1]) if token.startswith('"') else token
 position=0
 def section():
  nonlocal position
  result={}
  while position<len(tokens):
   key=tokens[position];position+=1
   if key=='}':return result
   if key=='{' or position>=len(tokens):raise ValueError('Invalid Steam library information.')
   token=tokens[position];position+=1
   result[value(key)]=section() if token=='{' else value(token)
  return result
 return section()

def steam_roots():
 roots=[]
 for hive,key,field in [(winreg.HKEY_CURRENT_USER,r'Software\Valve\Steam','SteamPath'),(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\WOW6432Node\Valve\Steam','InstallPath'),(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Valve\Steam','InstallPath')]:
  try:
   with winreg.OpenKey(hive,key) as handle:roots.append(pathlib.Path(winreg.QueryValueEx(handle,field)[0]))
  except OSError:pass
 for env in ('ProgramFiles(x86)','ProgramFiles'):
  if os.environ.get(env):roots.append(pathlib.Path(os.environ[env])/'Steam')
 return list(dict.fromkeys(p.resolve() for p in roots if p.is_dir()))

def normalize_game(path):
 path=pathlib.Path(path).expanduser().resolve()
 if path.is_file() and path.name.lower()==EXE.name.lower():path=path.parents[3]
 if path.name.lower()=='dungeons' and (path.parent/EXE).is_file():path=path.parent
 if not (path/EXE).is_file():raise ValueError('Choose the Minecraft Dungeons II folder that contains Dungeons.')
 return path

def discover_games():
 libraries=[]
 for steam in steam_roots():
  libraries.append(steam)
  for file in (steam/'steamapps/libraryfolders.vdf',steam/'config/libraryfolders.vdf'):
   if not file.is_file():continue
   try:
    library_data=vdf(file.read_text(encoding='utf-8-sig'))
    for key,value in library_data.get('libraryfolders',library_data.get('LibraryFolders',{})).items():
     if isinstance(value,dict) and value.get('path'):libraries.append(pathlib.Path(value['path']))
     elif key.isdecimal() and isinstance(value,str):libraries.append(pathlib.Path(value))
   except (OSError,ValueError):continue
 found=[]
 for library in dict.fromkeys(p.resolve() for p in libraries):
  manifest=library/'steamapps'/f'appmanifest_{APP_ID}.acf'
  if not manifest.is_file():continue
  try:
   data=vdf(manifest.read_text(encoding='utf-8-sig')).get('AppState',{})
   folder=data.get('installdir','')
   if not folder or pathlib.Path(folder).is_absolute() or '..' in pathlib.Path(folder).parts:continue
   found.append(normalize_game(library/'steamapps/common'/folder))
  except (OSError,ValueError):continue
 return list(dict.fromkeys(found))

def game():
 command="$ErrorActionPreference = 'Stop'; Get-Process | Where-Object { $_.ProcessName -eq 'Dungeons-Win64-Shipping' } | ForEach-Object { @{ pid=$_.Id; base=$_.MainModule.BaseAddress.ToInt64(); path=$_.MainModule.FileName } } | ConvertTo-Json -Compress"
 result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',command],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=15)
 if result.returncode:raise RuntimeError('Could not check whether the game is running.')
 data=json.loads(result.stdout) if result.stdout.strip() else None
 if isinstance(data,list):raise RuntimeError('More than one game is running. Close the extra game first.')
 return data

def worker_command(mode,*args):
 return ([sys.executable] if getattr(sys,'frozen',False) else [sys.executable,str(ROOT/'launcher.py')])+[mode,*args]

def worker_environment():
 environment=dict(os.environ)
 if getattr(sys,'frozen',False):environment['PYINSTALLER_RESET_ENVIRONMENT']='1'
 return environment

def settings():
 try:return json.loads((STATE/'settings.json').read_text())
 except (OSError,ValueError):return {}

def save_location(root):atomic_json(STATE/'settings.json',{'game_folder':str(normalize_game(root))})

def find_game():
 saved=settings().get('game_folder')
 if saved:
  try:return normalize_game(saved)
  except (OSError,ValueError):pass
 found=discover_games()
 if len(found)==1:return found[0]
 if len(found)>1:raise ValueError('Multiple installations found. Choose the game folder you want to use.')
 active=game()
 if active:return normalize_game(active['path'])
 raise ValueError('Game not found in Steam. Choose your Minecraft Dungeons II folder.')

def mod_folder(root):
 root=normalize_game(root);directory=root/'Dungeons/Content/Paks/~mods'
 if not directory.resolve().is_relative_to(root):raise ValueError('The mod folder points outside the selected game folder.')
 return directory

def manifest_path(root):
 identifier=hashlib.sha256(str(normalize_game(root)).casefold().encode()).hexdigest()[:16]
 return STATE/'installs'/(identifier+'.json')

def bundled_files():
 return {STEM+'.'+ext:ASSETS/(STEM+'.'+ext) for ext in EXTENSIONS}

def installed(root):
 directory=mod_folder(root)
 return all((directory/name).is_file() and digest(directory/name)==digest(source) for name,source in bundled_files().items())

def legacy_files(root):
 directory=mod_folder(root)
 if not directory.is_dir():return []
 known=json.loads((ASSETS/'legacy-hashes.json').read_text());result=[]
 for file in directory.iterdir():
  extension=file.suffix.lstrip('.').lower()
  if extension in known and file.is_file() and not file.is_symlink() and file.stat().st_size<100000 and file.name not in bundled_files() and digest(file)==known[extension]:result.append(file)
 return result

def verify_build(root):
 if digest(normalize_game(root)/EXE)!=EXPECTED:raise ValueError('This game update is not supported yet. No files were changed.')

def closed():
 if game():raise ValueError('Close Minecraft Dungeons II, then try again. The game has these mod files loaded.')

def backup_path(root,name):
 directory=STATE/'backups'/manifest_path(root).stem
 return directory/(hashlib.sha256(name.encode()).hexdigest()+'.backup')

def read_manifest(root):
 try:return json.loads(manifest_path(root).read_text())
 except FileNotFoundError:return {'files':{}}

def install_mod(root):
 root=normalize_game(root);verify_build(root)
 if installed(root) and not legacy_files(root):return False
 closed();directory=mod_folder(root);directory.mkdir(parents=True,exist_ok=True)
 previous=read_manifest(root);records=dict(previous.get('files',{}));before={};legacy=legacy_files(root)
 targets={name:(directory/name,source) for name,source in bundled_files().items()}
 for name,(target,source) in targets.items():
  if target.is_symlink():raise ValueError('An existing mod file is a link; choose a regular game installation.')
  current=target.read_bytes() if target.exists() else None;before[target]=current
  prior=records.get(name)
  if current is not None and (prior is None or hashlib.sha256(current).hexdigest()!=prior['installed_sha256']):
   backup=backup_path(root,name);backup.parent.mkdir(parents=True,exist_ok=True)
   backup.write_bytes(current);records[name]={'backup':str(backup),'backup_sha256':hashlib.sha256(current).hexdigest()}
  else:records[name]=dict(prior or {})
  records[name]['installed_sha256']=digest(source)
 for old in legacy:before[old]=old.read_bytes()
 record={'game_folder':str(root),'files':records,'legacy_files':{p.name:hashlib.sha256(before[p]).hexdigest() for p in legacy},'phase':'installing'}
 atomic_json(manifest_path(root),record)
 try:
  # Stage all payloads before replacing any installed file.
  staged=[]
  for name,(target,source) in targets.items():
   temporary=target.with_name(target.name+'.'+uuid.uuid4().hex+'.tmp');shutil.copyfile(source,temporary);staged.append((temporary,target))
  for temporary,target in staged:temporary.replace(target)
  for old in legacy:old.unlink()
  if not installed(root):raise OSError('The installed files could not be verified.')
  record['phase']='installed';atomic_json(manifest_path(root),record);save_location(root)
 except BaseException:
  for path,content in before.items():
   if content is None:path.unlink(missing_ok=True)
   else:path.write_bytes(content)
  atomic_json(manifest_path(root),previous)
  raise
 finally:
  for temporary,_ in locals().get('staged',[]):temporary.unlink(missing_ok=True)
 return True

def remove_mod(root):
 root=normalize_game(root);closed();directory=mod_folder(root);record=read_manifest(root)
 restore=[];remove=[]
 for name,source in bundled_files().items():
  target=directory/name;entry=record.get('files',{}).get(name,{})
  if target.is_symlink():raise ValueError('A mod file is a link; it was left untouched.')
  if target.exists() and digest(target) not in {digest(source),entry.get('installed_sha256')}:
   raise ValueError('A mod file was changed outside this launcher. It was left untouched: '+name)
  if entry.get('backup'):
   backup=pathlib.Path(entry['backup'])
   if not backup.resolve().is_relative_to((STATE/'backups').resolve()) or not backup.is_file() or digest(backup)!=entry['backup_sha256']:raise ValueError('The original-file backup is missing or changed. No files were removed.')
   restore.append((target,backup))
  elif target.exists():remove.append(target)
 remove.extend(legacy_files(root))
 for target,backup in restore:shutil.copyfile(backup,target)
 for path in remove:path.unlink()
 manifest_path(root).unlink(missing_ok=True)
 return len(remove)+len(restore)

def enable_estimates():
 from inventory_estimates import install,start_updater
 active=game()
 if not active:raise ValueError('The game is not running yet.')
 if digest(active['path'])!=EXPECTED:raise ValueError('This game update is not supported yet.')
 STATE.mkdir(parents=True,exist_ok=True)
 result=install(active);start_updater();return result

def install_and_play(root,notify,cancel):
 root=normalize_game(root);active=game()
 if active and normalize_game(active['path'])!=root:raise ValueError('A different installation is running. Close it first.')
 notify('Setting up the mod…');install_mod(root)
 notify('Mod installed. Waiting for the game…')
 if cancel.is_set():return
 if not active:notify('Opening Minecraft Dungeons II through Steam…');os.startfile('steam://rungameid/'+APP_ID)
 deadline=time.monotonic()+300;last='Open your character and inventory to enable the damage display.'
 while time.monotonic()<deadline and not cancel.is_set():
  active=game()
  if active:
   if normalize_game(active['path'])!=root:raise ValueError('Steam opened a different game installation.')
   result_file=STATE/('enable-'+uuid.uuid4().hex+'.json')
   try:
    process=subprocess.Popen(worker_command('--enable','--result-file',str(result_file)),env=worker_environment(),creationflags=subprocess.CREATE_NO_WINDOW)
    while process.poll() is None:
     if cancel.wait(.2):return
    result=json.loads(result_file.read_text()) if result_file.exists() else {'ok':False,'error':'The damage display could not start.'}
    if result.get('ok'):notify('Ready! Damage estimates are enabled in inventory.');return
    last=result.get('error',last)
    if last!='Unsupported object layout.' and any(s in last for s in ('not supported','Another adapter','layout','changed','Unexpected')):raise RuntimeError(last)
    notify('Mod installed. Open your character and inventory…')
   finally:result_file.unlink(missing_ok=True)
  cancel.wait(2)
 if not cancel.is_set():raise RuntimeError('Mod installed. Press Install & Play again after opening your character. '+last)
