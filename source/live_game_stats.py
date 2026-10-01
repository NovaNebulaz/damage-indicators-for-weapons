"""Read only access to the tested game's reflected player stats and visible UI."""
import ctypes
import functools
import math
import struct
import time

class GameReader:
    def __init__(self, pid, base):
        self.pid = pid; self.base = base
        self.ga = base+0xbea8bf0; self.pool = base+0xbdc5040
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.k.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        self.k.OpenProcess.restype = ctypes.c_void_p
        self.k.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.k.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        self.k.CloseHandle.argtypes = [ctypes.c_void_p]
        self.handle = self.k.OpenProcess(0x410, False, pid)
        if not self.handle:
            raise OSError('Could not read the running game.')
        self.attrs = {}; self.widgets = []; self.curve = None; self.last_scan = 0

    def close(self):
        if self.handle:
            self.k.CloseHandle(self.handle); self.handle = None
        self.name.cache_clear(); self.fields.cache_clear()

    def alive(self):
        code = ctypes.c_ulong()
        return bool(self.handle and self.k.GetExitCodeProcess(self.handle, ctypes.byref(code)) and code.value == 259)

    def read(self, address, size):
        if not 0 < address < 0x800000000000 or not 0 < size < 0x200000:
            raise ValueError('Invalid live address.')
        buf = ctypes.create_string_buffer(size); got = ctypes.c_size_t()
        if not self.k.ReadProcessMemory(self.handle, address, buf, size, ctypes.byref(got)) or got.value != size:
            raise OSError('The live game data changed. Refreshing…')
        return buf.raw

    def q(self, a): return struct.unpack('<Q', self.read(a,8))[0]
    def u(self, a): return struct.unpack('<I', self.read(a,4))[0]

    @functools.lru_cache(maxsize=8192)
    def name(self, ix):
        entry = self.q(self.pool+16+(ix>>16)*8)+(ix&65535)*2
        head = struct.unpack('<H',self.read(entry,2))[0]; length = head>>6
        if not 0 < length < 1024: raise ValueError('Invalid name.')
        return self.read(entry+2,length*(2 if head&1 else 1)).decode('utf-16-le' if head&1 else 'utf-8')

    def object_name(self, p): return self.name(self.u(p+24)) if p else ''
    def class_name(self, p): return self.object_name(self.q(p+16))

    @functools.lru_cache(maxsize=1024)
    def fields(self, cl):
        result = {}; visited = set()
        while cl and cl not in visited:
            visited.add(cl); fp = self.q(cl+0x50); seen = set()
            while fp and fp not in seen:
                seen.add(fp); raw = self.read(fp,0x78)
                result.setdefault(self.name(struct.unpack_from('<I',raw,32)[0]),struct.unpack_from('<I',raw,72)[0])
                fp = struct.unpack_from('<Q',raw,24)[0]
            cl = self.q(cl+0x40)
        return result

    def objects(self):
        total = self.u(self.ga+0x24); chunks = self.q(self.ga+16)
        if not 0 < total < 2000000: raise ValueError('Unsupported object layout.')
        for ci in range((total+65535)//65536):
            count = min(65536,total-ci*65536)
            raw = self.read(self.q(chunks+ci*8),count*24)
            for ii in range(count):
                p = struct.unpack_from('<Q',raw,ii*24)[0]
                if p: yield p

    def scan(self):
        attrs = {}; groups = {}; tables = []
        for p in self.objects():
            try:
                if self.u(p+8)&0x30: continue # Default objects and templates are never live UI.
                cl = self.q(p+16); cn = self.object_name(cl)
                if cn in ('ATR_Damage','ATR_ItemPower'):
                    owner = self.q(p+32)
                    if self.class_name(owner) in ('BP_AlexCharacter_C','BP_SteveCharacter_C'):
                        attrs.setdefault(owner,{})[cn] = (p,cl,self.fields(cl))
                elif cn in ('W_DamageIndicators_C','W_TooltipModule_Power_C'):
                    outer = self.q(p+32)
                    if self.object_name(outer) != 'WidgetTree': continue
                    owner = self.q(outer+32)
                    if self.class_name(owner) != 'W_Tooltip_C': continue
                    field = 'PrimaryStatText' if cn=='W_DamageIndicators_C' else 'PowerText'
                    groups.setdefault(owner,{})[field] = (p,cl,self.fields(cl)[field])
                elif 'DataTable' in cn and self.object_name(p)=='DT_GameBalanceDefinition':
                    tables.append(p)
            except (OSError, ValueError, UnicodeError, KeyError, struct.error):
                continue
        players = [v for v in attrs.values() if set(v)=={'ATR_Damage','ATR_ItemPower'}]
        if len(players)!=1: raise ValueError('Waiting for one local player…')
        self.attrs = players[0]
        self.widgets = [v for v in groups.values() if set(v)=={'PrimaryStatText','PowerText'}]
        self.curve = None
        for table in tables:
            count = self.u(table+56); rows = self.q(table+48)
            if not 0 < count <= 32: continue
            for i in range(count):
                raw = self.read(rows+i*24,16)
                if self.name(struct.unpack_from('<I',raw)[0])!='SecondPass': continue
                row = struct.unpack_from('<Q',raw,8)[0]
                constants = struct.unpack('<3f',self.read(row+48,12))
                if 0 < constants[0] < 10 and 0 < constants[1] < 1 and 0 < constants[2] < constants[0]:
                    self.curve = constants
        self.last_scan = time.monotonic()

    def visible(self, p):
        seen = set(); compared = False; priority = 0
        while p and p not in seen and len(seen)<64:
            seen.add(p)
            cn = self.class_name(p)
            if 'GeneratedClass' in cn or cn=='Class': return False,0
            if self.read(p+220,1)[0] in (1,2): return False,0
            if cn=='W_ComparedItemTooltip_C': compared = True
            if self.object_name(p)=='HoveredItemTooltip': priority = 2
            elif self.object_name(p)=='CompactTooltip': priority = max(priority,1)
            slot = self.q(p+48)
            sf = self.fields(self.q(slot+16)) if slot else {}
            if slot and sf.get('Parent'):
                p = self.q(slot+sf['Parent'])
            else:
                outer = self.q(p+32)
                if outer and self.object_name(outer)=='WidgetTree': p = self.q(outer+32)
                else: break
        return not compared, priority

    def text(self, widget, offset, pattern):
        text_widget = self.q(widget+offset)
        if not text_widget: return ''
        tf = self.fields(self.q(text_widget+16)).get('Text')
        if not tf: return ''
        data = self.q(text_widget+tf)
        if not data: return ''
        # Formatted and pooled text use distinct layouts; validate the content.
        for off in (24,32):
            try:
                ptr,num,cap = struct.unpack('<QII',self.read(data+off,16))
                if not 0 < num <= cap <= 512: continue
                value = self.read(ptr,num*2).decode('utf-16-le').rstrip('\0')
                if pattern(value): return value
            except (OSError, ValueError, UnicodeError): continue
        return ''

    def attribute_values(self, name):
        p,cl,fields = self.attrs[name]
        if self.q(p+16)!=cl: raise ValueError('Player changed. Refreshing…')
        raw = self.read(p,max(fields.values())+16)
        values = {n:struct.unpack_from('<f',raw,off+12)[0] for n,off in fields.items() if off>=40}
        if not all(math.isfinite(v) for v in values.values()): raise ValueError('Invalid live stats.')
        return values

