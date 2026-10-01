import pathlib,struct,json

from keystone import Ks,KS_ARCH_X86,KS_MODE_64
ROOT=pathlib.Path(__file__).resolve().parents[1]/'assets'
CONTROL=0x1111222233334444
CONVERT=0x3333444455556666
HANDLER=0x4444555566667777
FONT_COPY=0x5555666677778888
FONT_SET=0x6666777788889999
def words(v):return '.byte '+','.join(str(x) for x in (v+'\0').encode('utf-16-le'))
def boost(offset):return f'cvtss2sd xmm3, dword ptr [r15+{offset+12}]\n mulsd xmm2,xmm3\n'
def line(label,low=0x70,high=0x78,mult=None):
 return f'lea rsi,[rip+{label}]\n call append_text\n movsd xmm0,[rsp+{low}]\n movsd xmm1,[rsp+{high}]\n'+(f'mulsd xmm0,[rsp+{mult}]\n mulsd xmm1,[rsp+{mult}]\n' if mult else '')+'call append_range\n'
source=f'''
vm_entry:
 mov r8,[rdx+8]
 mov rdx,[rdx]
 jmp raw_entry
 .align 16
raw_entry:
 push rbx
 push rsi
 push rdi
 push r12
 push r13
 push r14
 push r15
 sub rsp,0x460
 mov [rsp+0x20],rcx
 mov rbx,rdx
 mov rsi,r8
 cmp byte ptr [rcx+0x18],0
 jne finish
 cmp qword ptr [rbx+0x4a0],0
 je finish
 mov r12,{CONTROL}
 inc qword ptr [r12+16]
 mov [r12+24],rbx
 mov [r12+64],rsi
 mov dword ptr [r12+44],0
 mov eax,[rsi+240]
 mov [r12+32],eax
 mov rdx,[rsi+40]
 mov [r12+56],rdx
 lea rdi,[rsp+0x100]
 mov word ptr [rdi],0
 cmp eax,1
 jl render
 cmp eax,999
 jg render
 mov r14,[r12]
 mov r15,[r12+8]
 test r14,r14
 je render
 test r15,r15
 je render
 mov ecx,[r14]
 cmp ecx,350
 ja render
 cmp dword ptr [r14+4],64
 jne render
 dec eax
 cvtsi2sd xmm2,eax
 mulsd xmm2,[r14+8]
 addsd xmm2,[rip+one]
 add r14,16
lookup:
 test ecx,ecx
 je render
 cmp [r14],rdx
 je found
 add r14,64
 dec ecx
 jmp lookup
found:
 mov r13d,[r14+8]
 mov [r12+44],r13d
 {boost(144)}
 {boost(704)}
 {boost(736)}
 cmp r13d,1
 jne ranged_boost
 {boost(160)}
 {boost(176)}
 cvtss2sd xmm4,dword ptr [r15+604]
 jmp common_boost
ranged_boost:
 cmp r13d,2
 jne render
 {boost(224)}
 {boost(240)}
 cvtss2sd xmm4,dword ptr [r15+620]
common_boost:
 cvtss2sd xmm3,dword ptr [r15+588]
 mulsd xmm4,xmm3
 movsd [rsp+0xa0],xmm4
 cvtss2sd xmm3,dword ptr [r15+780]
 movsd [rsp+0xa8],xmm3
 movsd [rsp+0x90],xmm2
 cvtss2sd xmm3,dword ptr [r15+764]
 movsd xmm0,[r14+16]
 movsd xmm1,[r14+24]
 addsd xmm0,xmm3
 addsd xmm1,xmm3
 mulsd xmm0,xmm2
 mulsd xmm1,xmm2
 movsd [rsp+0x70],xmm0
 movsd [rsp+0x78],xmm1
 cmp r13d,1
 jne ranged_lines
 {line('normal_label')}
 {line('crit_label',mult=0xa0)}
 jmp conditional
ranged_lines:
 {line('quick_label')}
 test dword ptr [r14+12],1
 jz ranged_crit
 movsd xmm0,[r14+16]
 movsd xmm1,[r14+24]
 mulsd xmm0,[r14+32]
 mulsd xmm1,[r14+32]
 cvtss2sd xmm3,dword ptr [r15+764]
 addsd xmm0,xmm3
 addsd xmm1,xmm3
 movsd xmm2,[rsp+0x90]
 {boost(640)}
 mulsd xmm0,xmm2
 mulsd xmm1,xmm2
 movsd [rsp+0x80],xmm0
 movsd [rsp+0x88],xmm1
 {line('charged_label',0x80,0x88)}
ranged_crit:
 {line('crit_quick_label',mult=0xa0)}
 test dword ptr [r14+12],1
 jz conditional
 {line('crit_charged_label',0x80,0x88,0xa0)}
conditional:
 movsd xmm0,[rsp+0xa8]
 ucomisd xmm0,[rip+one]
 je volley
 jp volley
 {line('full_label',mult=0xa8)}
 cmp r13d,2
 jne volley
 test dword ptr [r14+12],1
 jz volley
 {line('full_charged_label',0x80,0x88,0xa8)}
volley:
 cmp r13d,2
 jne footnote
 cmp dword ptr [r14+40],1
 jbe footnote
 lea rsi,[rip+projectile_label]
 call append_text
 mov eax,[r14+40]
 call append_number
footnote:
 lea rsi,[rip+neutral_label]
 call append_text
render:
 mov word ptr [rdi],0
 pxor xmm0,xmm0
 movdqu [rsp+0x30],xmm0
 lea rax,[rsp+0x100]
 mov [rsp+0x40],rax
 sub rdi,rax
 shr edi,1
 inc edi
 mov [rsp+0x48],edi
 mov [rsp+0x4c],edi
 lea rcx,[rsp+0x30]
 lea rdx,[rsp+0x40]
 mov rax,{CONVERT}
 call rax
 mov rcx,[rsp+0x20]
 mov rdx,rbx
 lea r8,[rsp+0x30]
 mov rax,{HANDLER}
 call rax
 mov rcx,[rbx+0x4a0]
 test rcx,rcx
 je finish
 lea rdx,[rcx+464]
 lea rcx,[rsp+0x100]
 mov rax,{FONT_COPY}
 call rax
 mov dword ptr [rsp+0x148],0x42000000
 mov rcx,[rbx+0x4a0]
 lea rdx,[rsp+0x100]
 mov rax,{FONT_SET}
 call rax
finish:
 add rsp,0x460
 pop r15
 pop r14
 pop r13
 pop r12
 pop rdi
 pop rsi
 pop rbx
 ret
append_text:
 movzx eax,word ptr [rsi]
 test eax,eax
 jz text_done
 mov [rdi],ax
 add rsi,2
 add rdi,2
 jmp append_text
text_done:
 ret
append_range:
 call round_number
 mov r9d,eax
 call append_number
 movsd xmm0,xmm1
 call round_number
 cmp eax,r9d
 je range_done
 mov word ptr [rdi],32
 mov word ptr [rdi+2],45
 mov word ptr [rdi+4],32
 add rdi,6
 call append_number
range_done:
 ret
round_number:
 xorpd xmm5,xmm5
 maxsd xmm0,xmm5
 minsd xmm0,[rip+ceiling]
 addsd xmm0,[rip+half]
 cvttsd2si eax,xmm0
 ret
append_number:
 xor edx,edx
 mov r8d,10
 div r8d
 push rdx
 test eax,eax
 jz emit_digit
 call append_number
emit_digit:
 pop rdx
 add dx,48
 mov [rdi],dx
 add rdi,2
 ret
normal_label:
 {words('Est. normal ')}
quick_label:
 {words('Est. quick ')}
charged_label:
 {words(chr(10)+'Charged ')}
crit_label:
 {words(chr(10)+'Critical ')}
crit_quick_label:
 {words(chr(10)+'Crit quick ')}
crit_charged_label:
 {words(chr(10)+'Crit charged ')}
full_label:
 {words(chr(10)+'Full HP ')}
full_charged_label:
 {words(chr(10)+'Full HP charged ')}
projectile_label:
 {words(chr(10)+'Per projectile; count ')}
neutral_label:
 {words(chr(10)+'Current boosts; neutral target')}
 .align 8
one:
 .quad 0x3ff0000000000000
half:
 .quad 0x3fe0000000000000
ceiling:
 .quad 0x41cdcd6500000000
'''
binary=bytes(Ks(KS_ARCH_X86,KS_MODE_64).asm(source)[0]);assert len(binary)<4096
patches={}
for name,value in [('control',CONTROL),('convert',CONVERT),('handler',HANDLER),('font_copy',FONT_COPY),('font_set',FONT_SET)]:
 needle=struct.pack('<Q',value);assert binary.count(needle)==1;patches[name]=binary.index(needle)
ROOT.joinpath('estimate_hook.bin').write_bytes(binary)
ROOT.joinpath('estimate_hook.json').write_text(json.dumps({'patches':patches,'raw_offset':16,'vm_offset':0,'version':2,'revision':7},indent=2))
pathlib.Path(__file__).with_name('formatter.asm').write_text(source)
print('Built definition-based formatter',len(binary),'bytes',patches)
