
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
 mov r12,1229801703532086340
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
 cvtss2sd xmm3, dword ptr [r15+156]
 mulsd xmm2,xmm3

 cvtss2sd xmm3, dword ptr [r15+716]
 mulsd xmm2,xmm3

 cvtss2sd xmm3, dword ptr [r15+748]
 mulsd xmm2,xmm3

 cmp r13d,1
 jne ranged_boost
 cvtss2sd xmm3, dword ptr [r15+172]
 mulsd xmm2,xmm3

 cvtss2sd xmm3, dword ptr [r15+188]
 mulsd xmm2,xmm3

 cvtss2sd xmm4,dword ptr [r15+604]
 jmp common_boost
ranged_boost:
 cmp r13d,2
 jne render
 cvtss2sd xmm3, dword ptr [r15+236]
 mulsd xmm2,xmm3

 cvtss2sd xmm3, dword ptr [r15+252]
 mulsd xmm2,xmm3

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
 lea rsi,[rip+normal_label]
 call append_text
 movsd xmm0,[rsp+112]
 movsd xmm1,[rsp+120]
call append_range

 lea rsi,[rip+crit_label]
 call append_text
 movsd xmm0,[rsp+112]
 movsd xmm1,[rsp+120]
mulsd xmm0,[rsp+160]
 mulsd xmm1,[rsp+160]
call append_range

 jmp conditional
ranged_lines:
 lea rsi,[rip+quick_label]
 call append_text
 movsd xmm0,[rsp+112]
 movsd xmm1,[rsp+120]
call append_range

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
 cvtss2sd xmm3, dword ptr [r15+652]
 mulsd xmm2,xmm3

 mulsd xmm0,xmm2
 mulsd xmm1,xmm2
 movsd [rsp+0x80],xmm0
 movsd [rsp+0x88],xmm1
 lea rsi,[rip+charged_label]
 call append_text
 movsd xmm0,[rsp+128]
 movsd xmm1,[rsp+136]
call append_range

ranged_crit:
 lea rsi,[rip+crit_quick_label]
 call append_text
 movsd xmm0,[rsp+112]
 movsd xmm1,[rsp+120]
mulsd xmm0,[rsp+160]
 mulsd xmm1,[rsp+160]
call append_range

 test dword ptr [r14+12],1
 jz conditional
 lea rsi,[rip+crit_charged_label]
 call append_text
 movsd xmm0,[rsp+128]
 movsd xmm1,[rsp+136]
mulsd xmm0,[rsp+160]
 mulsd xmm1,[rsp+160]
call append_range

conditional:
 movsd xmm0,[rsp+0xa8]
 ucomisd xmm0,[rip+one]
 je volley
 jp volley
 lea rsi,[rip+full_label]
 call append_text
 movsd xmm0,[rsp+112]
 movsd xmm1,[rsp+120]
mulsd xmm0,[rsp+168]
 mulsd xmm1,[rsp+168]
call append_range

 cmp r13d,2
 jne volley
 test dword ptr [r14+12],1
 jz volley
 lea rsi,[rip+full_charged_label]
 call append_text
 movsd xmm0,[rsp+128]
 movsd xmm1,[rsp+136]
mulsd xmm0,[rsp+168]
 mulsd xmm1,[rsp+168]
call append_range

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
 mov rax,3689367580026693222
 call rax
 mov rcx,[rsp+0x20]
 mov rdx,rbx
 lea r8,[rsp+0x30]
 mov rax,4919150518273996663
 call rax
 mov rcx,[rbx+0x4a0]
 test rcx,rcx
 je finish
 lea rdx,[rcx+464]
 lea rcx,[rsp+0x100]
 mov rax,6148933456521300104
 call rax
 mov dword ptr [rsp+0x148],0x42000000
 mov rcx,[rbx+0x4a0]
 lea rdx,[rsp+0x100]
 mov rax,7378716394768603545
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
 .byte 69,0,115,0,116,0,46,0,32,0,110,0,111,0,114,0,109,0,97,0,108,0,32,0,0,0
quick_label:
 .byte 69,0,115,0,116,0,46,0,32,0,113,0,117,0,105,0,99,0,107,0,32,0,0,0
charged_label:
 .byte 10,0,67,0,104,0,97,0,114,0,103,0,101,0,100,0,32,0,0,0
crit_label:
 .byte 10,0,67,0,114,0,105,0,116,0,105,0,99,0,97,0,108,0,32,0,0,0
crit_quick_label:
 .byte 10,0,67,0,114,0,105,0,116,0,32,0,113,0,117,0,105,0,99,0,107,0,32,0,0,0
crit_charged_label:
 .byte 10,0,67,0,114,0,105,0,116,0,32,0,99,0,104,0,97,0,114,0,103,0,101,0,100,0,32,0,0,0
full_label:
 .byte 10,0,70,0,117,0,108,0,108,0,32,0,72,0,80,0,32,0,0,0
full_charged_label:
 .byte 10,0,70,0,117,0,108,0,108,0,32,0,72,0,80,0,32,0,99,0,104,0,97,0,114,0,103,0,101,0,100,0,32,0,0,0
projectile_label:
 .byte 10,0,80,0,101,0,114,0,32,0,112,0,114,0,111,0,106,0,101,0,99,0,116,0,105,0,108,0,101,0,59,0,32,0,99,0,111,0,117,0,110,0,116,0,32,0,0,0
neutral_label:
 .byte 10,0,67,0,117,0,114,0,114,0,101,0,110,0,116,0,32,0,98,0,111,0,111,0,115,0,116,0,115,0,59,0,32,0,110,0,101,0,117,0,116,0,114,0,97,0,108,0,32,0,116,0,97,0,114,0,103,0,101,0,116,0,0,0
 .align 8
one:
 .quad 0x3ff0000000000000
half:
 .quad 0x3fe0000000000000
ceiling:
 .quad 0x41cdcd6500000000
