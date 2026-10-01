"""Read weapon definitions for the verified executable; no calibration values."""
import math,struct,time

TABLES=('DT_MeleePropertyDefinition','DT_RangedPropertyDefinition','DT_ProjectileDefinition')
ITEM_TABLES=('DT_ItemDefinitionMelee','DT_ItemDefinitionRanged')

def discover(reader):
 tables={};types={}
 for p in reader.objects():
  try:
   name=reader.object_name(p);cn=reader.class_name(p)
   if name in TABLES+ITEM_TABLES and 'DataTable' in cn:tables[name]=p
   elif name=='ItemTableRow' and cn=='ScriptStruct':types[name]=(reader.fields(p),reader.u(p+0x58))
   elif name in ('MeleeAttackVariant','RangedAttackProjectileSpawnDescription','MeleePropertyTableRow','RangedPropertyTableRow','ProjectileTableRow','BaseProjectileGameplayData') and cn=='ScriptStruct':types[name]=(reader.fields(p),reader.u(p+0x58))
  except (OSError,ValueError,UnicodeError):pass
 required={'MeleeAttackVariant':({'Damage':56,'DamageType':12,'AdditionalDamageTypes':24},328),'RangedAttackProjectileSpawnDescription':({'ProjectileTypeTag':0,'NumberOfProjectiles':8},64),'MeleePropertyTableRow':({'AttackVariants':184},768),'RangedPropertyTableRow':({'AttackDefintion':184},720),'ProjectileTableRow':({'ProjectileGameplayData':456},1080),'BaseProjectileGameplayData':({'Damage':288},496)}
 for name,(fields,size) in required.items():
  if name not in types or any(types[name][0].get(n)!=o for n,o in fields.items()):raise ValueError('Weapon definition layout changed.')
  if name in ('MeleeAttackVariant','RangedAttackProjectileSpawnDescription') and types[name][1]!=size:raise ValueError('Attack definition size changed.')
 if types.get('ItemTableRow',({},0))[0].get('IconReference')!=312:raise ValueError('Item icon definition layout changed.')
 if set(tables)!=set(TABLES+ITEM_TABLES):raise ValueError('Weapon definitions unavailable.')
 result={};projectiles={}
 def rows(table):
  data=reader.q(table+48);count=reader.u(table+56)
  if not 0<count<4096:raise ValueError('Unexpected weapon table.')
  for i in range(count):
   raw=reader.read(data+i*24,16);p=struct.unpack_from('<Q',raw,8)[0]
   if p:yield p
 def f(p):return struct.unpack('<f',reader.read(p,4))[0]
 for p in rows(tables['DT_ProjectileDefinition']):projectiles[reader.q(p+8)]=f(p+744)
 for p in rows(tables['DT_MeleePropertyDefinition']):
  tag=reader.q(p+8);data=reader.q(p+184);count=reader.u(p+192)
  if count==0:continue
  if not 0<count<=16:raise ValueError('Unexpected melee combo.')
  variants=[f(data+i*328+56) for i in range(count)]
  result[tag]={'kind':1,'low':min(variants),'high':max(variants),'charge':0.0,'projectiles':1,'name':reader.name(tag&0xffffffff)}
 for p in rows(tables['DT_RangedPropertyDefinition']):
  tag=reader.q(p+8);attack=p+184;volleys=reader.q(attack+24);nv=reader.u(attack+32)
  if nv==0:continue
  if not 0<nv<=16:raise ValueError('Unexpected ranged volley.')
  damage=[];total=0
  for i in range(nv):
   data=reader.q(volleys+i*16);count=reader.u(volleys+i*16+8)
   if not 0<count<=16:raise ValueError('Unexpected projectile definition.')
   for j in range(count):
    q=data+j*64;pt=reader.q(q);number=reader.u(q+8)
    if pt not in projectiles or not 1<=number<=64:raise ValueError('Unresolved projectile damage.')
    damage.append(projectiles[pt]*f(attack+72));total+=number
  charge=f(attack+60) if f(attack+48)>0 else 0.0
  result[tag]={'kind':2,'low':min(damage),'high':max(damage),'charge':charge,'projectiles':total,'name':reader.name(tag&0xffffffff)}
 for value in result.values():
  if not all(math.isfinite(value[n]) for n in ('low','high','charge')) or not 0<value['low']<=value['high']<100000:raise ValueError('Invalid weapon definition.')
 # TSoftObjectPtr's asset package FName is its path at +8. The tooltip carries
 # the same pointer, independently of localization or weapon category enum.
 icons={}
 for table in ITEM_TABLES:
  for p in rows(tables[table]):
   tag=reader.q(p+8)
   if tag not in result:continue
   icon=reader.q(p+320)
   if not icon:raise ValueError('Weapon icon is missing.')
   if icon in icons:raise ValueError('Ambiguous weapon icon; no estimate installed.')
   icons[icon]=result[tag]
 if len(icons)!=len(result):
  mapped={v['name'] for v in icons.values()}
  reader.weapon_unmapped=[v['name'] for v in result.values() if v['name'] not in mapped]
 if len(icons)<40:raise ValueError('Weapon tooltip definitions unavailable.')
 reader.weapon_definitions=icons;reader.weapon_scan_time=time.monotonic()
 return icons

def bank(reader):
 definitions=getattr(reader,'weapon_definitions',None)
 if not definitions or time.monotonic()-getattr(reader,'weapon_scan_time',0)>30:definitions=discover(reader)
 # Active GameBalanceDefinition pointer used by the game's damage-number conversion.
 settings=reader.q(reader.base+0xbb3ea08);fudge=struct.unpack('<f',reader.read(settings+56,4))[0]
 if not math.isfinite(fudge) or not 0<=fudge<=1:raise ValueError('Damage-number settings unavailable.')
 result=bytearray(struct.pack('<IId',len(definitions),64,fudge))
 for tag,v in definitions.items():
  flags=(1 if v['charge']>0 else 0)|(2 if v['projectiles']>1 else 0)
  result.extend(struct.pack('<QIIdddII16x',tag,v['kind'],flags,v['low'],v['high'],v['charge'],v['projectiles'],0))
 if len(result)>24000:raise ValueError('Too many weapon definitions.')
 return bytes(result)
