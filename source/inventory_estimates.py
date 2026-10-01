"""Inventory damage formatter and background weapon-definition updater."""
import ctypes,hashlib,json,pathlib,struct,subprocess,sys,time,os
from live_game_stats import GameReader
from weapon_data import bank

ROOT=pathlib.Path(__file__).resolve().parent
from mod_manager import STATE, game, EXPECTED, SUPPORTED, worker_command,worker_environment
RECORD=STATE/'adapter-session.json'
META=json.loads((ROOT/'assets/estimate_hook.json').read_text())
TEMPLATE=(ROOT/'assets/estimate_hook.bin').read_bytes()

class Writer:
 def __init__(self,pid):
  self.k=ctypes.WinDLL('kernel32',use_last_error=True)
  self.k.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong];self.k.OpenProcess.restype=ctypes.c_void_p
  self.k.WriteProcessMemory.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
  self.k.VirtualAllocEx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_ulong,ctypes.c_ulong];self.k.VirtualAllocEx.restype=ctypes.c_void_p
  self.k.VirtualProtectEx.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_ulong,ctypes.POINTER(ctypes.c_ulong)]
  self.k.FlushInstructionCache.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t]
  self.k.CloseHandle.argtypes=[ctypes.c_void_p]
  self.handle=self.k.OpenProcess(0x438,False,pid)
  if not self.handle:raise ctypes.WinError(ctypes.get_last_error())
 def write(self,p,data):
  buf=ctypes.create_string_buffer(data);size=ctypes.c_size_t()
  if not self.k.WriteProcessMemory(self.handle,p,buf,len(data),ctypes.byref(size)) or size.value!=len(data):raise ctypes.WinError(ctypes.get_last_error())
 def allocate(self,size):
  p=self.k.VirtualAllocEx(self.handle,None,size,0x3000,0x04)
  if not p:raise ctypes.WinError(ctypes.get_last_error())
  return p
 def executable(self,p,size):
  old=ctypes.c_ulong()
  if not self.k.VirtualProtectEx(self.handle,p,size,0x20,ctypes.byref(old)):raise ctypes.WinError(ctypes.get_last_error())
  if not self.k.FlushInstructionCache(self.handle,p,size):raise ctypes.WinError(ctypes.get_last_error())
 def close(self):self.k.CloseHandle(self.handle)

def patched(base,control,layout=None):
 code=bytearray(TEMPLATE)
 layout=layout or {'convert':0x3e78e00,'handler':0x6659710,'font_copy':0x17863d0,'font_set':0x36f4720}
 targets={'control':control,**{n:base+layout[n] for n in ('convert','handler','font_copy','font_set')}}
 for name,offset in META['patches'].items():struct.pack_into('<Q',code,offset,targets[name])
 return bytes(code)

def entries(record):
 remote=int(record['adapter'],16)
 if record.get('version')==2:return (remote,remote+16,remote+16)
 return (remote+128,remote,remote)

def valid(reader,record):
 if record.get('pid')!=reader.pid or int(record['image_base'],16)!=reader.base:return False
 if reader.read(int(record['state_function'],16)+0x130,24)!=struct.pack('<3Q',*entries(record)):return False
 if record.get('version')==2:
  if record.get('code_sha256') and 0<record.get('code_length',0)<=4096:
   return hashlib.sha256(reader.read(int(record['adapter'],16),record['code_length'])).hexdigest()==record['code_sha256']
  return reader.read(int(record['adapter'],16),len(TEMPLATE))==patched(reader.base,int(record['control'],16))
 return reader.read(int(record['adapter'],16),4)==b'\x48\x83\xec\x68'

def cstring(reader,address):
 count=reader.u(address)
 if not 0<count<128:raise ValueError('Unsupported script metadata.')
 return reader.read(address+8 if count<=7 else reader.q(address+8),count).decode('ascii')

def find_handler(reader):
 found=[];structs={}
 for p in reader.objects():
  try:
   n=reader.object_name(p)
   if n=='AS_SpicewoodTooltipPrimaryStat':found.append(p)
   elif n in ('AS_TooltipState','AS_TooltipModule_Power','TextBlock','SlateFontInfo'):structs[n]=reader.fields(p)
  except (OSError,ValueError,UnicodeError):pass
 if len(found)!=1:raise ValueError('Waiting for the inventory script class…')
 if structs.get('AS_TooltipState',{}).get('ItemIconModule')!=32 or structs.get('AS_TooltipState',{}).get('PowerModule')!=216 or structs.get('AS_TooltipModule_Power',{}).get('PowerInteger')!=24:
  raise ValueError('The tooltip state layout differs from the verified build.')
 if structs.get('TextBlock',{}).get('Font')!=464 or structs.get('SlateFontInfo',{}).get('Size')!=72:raise ValueError('The font layout changed.')
 cl=found[0];typ=reader.q(reader.q(cl+0x280)+0xd0)
 if cstring(reader,typ+0x10)!='UAS_SpicewoodTooltipPrimaryStat' or reader.q(typ+0x60)!=cl:raise ValueError('Unexpected stat class.')
 if reader.u(typ+0x1e0)!=3:raise ValueError('Unexpected stat methods.')
 table=reader.q(typ+0x1d8);functions={}
 for i in range(3):
  fn=reader.q(table+i*8)
  if cstring(reader,fn+0x20)=='UpdateModule':
   param=reader.q(reader.q(fn+0x50)+8)
   functions[cstring(reader,param+0x10)]=fn
 if set(functions)!={'FAS_TooltipState','FText'}:raise ValueError('Unexpected stat overloads.')
 if reader.q(functions['FText']+0x140)!=reader.base+reader.layout['handler']:raise ValueError('Unexpected text handler.')
 return cl,functions['FAS_TooltipState'],functions['FText']

def seed(writer,reader,control,destination):
 if not reader.attrs or time.monotonic()-reader.last_scan>30:reader.scan()
 required={'BaseDamageMultiplier':144,'MeleeDamageMultiplier':160,'MeleeDamageSourceMultiplier':176,'RangedDamageMultiplier':224,'RangedDamageSourceMultiplier':240,'RangedChargedAttackMultiplier':640,'CriticalHitMultiplier':576,'CriticalHitMultiplierMelee':592,'CriticalHitMultiplierRanged':608,'AttackEmpowerment':704,'PrimaryTargetDamageMultiplier':736,'BaseDamageBonus':752,'FullHealthTargetDamageMultiplier':768}
 damage,cl,fields=reader.attrs['ATR_Damage']
 if any(fields.get(name)!=offset for name,offset in required.items()):raise ValueError('Unexpected boost layout.')
 reader.attribute_values('ATR_Damage')
 writer.write(destination,bank(reader))
 writer.write(control+8,struct.pack('<Q',damage))
 writer.write(control,struct.pack('<Q',destination))

def install(game):
 reader=GameReader(game['pid'],game['base']);writer=Writer(game['pid'])
 try:
  previous=json.loads(RECORD.read_text(encoding='utf-8-sig')) if RECORD.exists() else None
  if previous and valid(reader,previous) and previous.get('version')==2 and previous.get('revision')==META['revision']:return previous
  cl,state,text=find_handler(reader)
  current=reader.read(state+0x130,24);original=struct.pack('<3Q',*((reader.base+reader.layout['state_handler'],)*3))
  if current!=original and not (previous and valid(reader,previous) and int(previous['state_function'],16)==state):raise ValueError('Another adapter is active. No code was changed.')
  if reader.read(reader.base+reader.layout['convert'],12)!=bytes.fromhex('40534883ec30488b02488bd9'):raise ValueError('Text constructor changed.')
  if reader.read(reader.base+reader.layout['font_copy'],10)!=bytes.fromhex('48895c2408574883ec20') or reader.read(reader.base+reader.layout['font_set'],10)!=bytes.fromhex('48895c240848896c2410'):raise ValueError('Font functions changed.')
  remote=writer.allocate(4096);control=writer.allocate(65536)
  code=patched(reader.base,control,reader.layout)
  if code[16]!=0x53:raise ValueError('Invalid native adapter entry.')
  seed(writer,reader,control,control+0x1000)
  writer.write(remote,code);writer.executable(remote,4096)
  record={'pid':game['pid'],'image_base':hex(reader.base),'class':hex(cl),'state_function':hex(state),'text_function':hex(text),'native_text_handler':hex(reader.base+reader.layout['handler']),'adapter':hex(remote),'control':hex(control),'version':2,'revision':META['revision'],'code_length':len(code),'code_sha256':hashlib.sha256(code).hexdigest(),'original_bytes':original.hex(),'rollback_bytes':current.hex(),'applied':True}
  if reader.read(state+0x130,24)!=current:raise ValueError('The handler changed during preparation.')
  writer.write(state+0x130,struct.pack('<3Q',*entries(record)))
  if not valid(reader,record):
   writer.write(state+0x130,current);raise ValueError('Adapter verification failed; the previous adapter was restored.')
  (STATE/'previous-adapter-session.json').write_text(json.dumps(previous,indent=2))
  RECORD.write_text(json.dumps(record,indent=2))
  return record
 finally:reader.close();writer.close()

def update():
 record=json.loads(RECORD.read_text());reader=GameReader(record['pid'],int(record['image_base'],16));writer=Writer(record['pid'])
 control=int(record['control'],16);toggle=1
 try:
  while reader.alive() and valid(reader,record):
   try:
    destination=control+(0x9000 if toggle else 0x1000)
    seed(writer,reader,control,destination);toggle^=1
   except (OSError,ValueError,KeyError):
    writer.write(control,struct.pack('<Q',0));reader.attrs={};reader.widgets=[]
   time.sleep(0.75)
 finally:reader.close();writer.close()

def start_updater():
 subprocess.Popen(worker_command('--update'),cwd=STATE,env=worker_environment(),creationflags=subprocess.CREATE_NO_WINDOW)

def main():
 if '--update' in sys.argv:
  kernel=ctypes.WinDLL('kernel32',use_last_error=True)
  kernel.CreateMutexW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_wchar_p];kernel.CreateMutexW.restype=ctypes.c_void_p
  kernel.CloseHandle.argtypes=[ctypes.c_void_p]
  ctypes.set_last_error(0);mutex=kernel.CreateMutexW(None,False,'Local\\DamageIndicatorsForWeaponsUpdater')
  if not mutex:return
  attempts=0
  while ctypes.get_last_error()==183:
   kernel.CloseHandle(mutex);attempts+=1
   if attempts>=20:return
   time.sleep(0.25);ctypes.set_last_error(0)
   mutex=kernel.CreateMutexW(None,False,'Local\\DamageIndicatorsForWeaponsUpdater')
   if not mutex:return
  try:update()
  finally:kernel.CloseHandle(mutex)
  return
 active_game=game()
 if not active_game:raise ValueError('Start Minecraft Dungeons II through Steam first.')
 with pathlib.Path(active_game['path']).open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
 if digest not in SUPPORTED:raise ValueError('Game version changed. No adapter was installed.')
 result=install(active_game);start_updater();print(json.dumps(result,indent=2))

if __name__=='__main__':
 try:main()
 except Exception as error:
  if '--update' not in sys.argv:print(str(error),file=sys.stderr)
  sys.exit(1)
