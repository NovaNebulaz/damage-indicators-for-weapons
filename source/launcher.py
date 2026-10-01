"""A small Windows launcher for Damage Indicators for weapons."""
from __future__ import annotations
import json,os,queue,sys,threading,traceback
from mod_manager import TITLE,STATE,atomic_json,find_game,normalize_game,save_location,installed,install_and_play,remove_mod,game

def worker():
 STATE.mkdir(parents=True,exist_ok=True)
 result_path=None
 if '--result-file' in sys.argv:result_path=sys.argv[sys.argv.index('--result-file')+1]
 try:
  if '--update' in sys.argv:
   from inventory_estimates import main
   main()
  else:
   from mod_manager import enable_estimates
   enable_estimates()
  result={'ok':True}
 except Exception as error:
  result={'ok':False,'error':str(error)}
  with (STATE/'launcher.log').open('a',encoding='utf-8') as log:log.write(traceback.format_exc()+'\n')
 if result_path:
  from pathlib import Path
  target=Path(result_path)
  if target.resolve().parent==STATE.resolve():atomic_json(target,result)
 return 0 if result['ok'] else 1

def main():
 if '--update' in sys.argv or '--enable' in sys.argv:return worker()
 if '--diagnostics' in sys.argv:
  from mod_manager import discover_games
  result={'title':TITLE,'games':[str(p) for p in discover_games()]}
  if '--result-file' in sys.argv:
   from pathlib import Path
   target=Path(sys.argv[sys.argv.index('--result-file')+1]);atomic_json(target,result)
  else:print(json.dumps(result))
  return 0
 import ctypes,tkinter as tk
 from tkinter import ttk,filedialog,messagebox
 try:ctypes.windll.shcore.SetProcessDpiAwareness(1)
 except (AttributeError,OSError):pass
 STATE.mkdir(parents=True,exist_ok=True)
 window=tk.Tk();window.title(TITLE);window.geometry('670x500');window.minsize(610,500)
 try:
  from mod_manager import ASSETS
  window.iconbitmap(str(ASSETS/'launcher.ico'))
 except tk.TclError:pass
 window.configure(bg='#101b23')
 style=ttk.Style(window);style.theme_use('clam')
 style.configure('TButton',font=('Segoe UI',10),padding=(14,9),background='#23343f',foreground='#eef6f8',borderwidth=0)
 style.map('TButton',background=[('active','#304652'),('disabled','#192b35')],foreground=[('disabled','#71818b')])
 style.configure('Play.TButton',font=('Segoe UI Semibold',11),background='#55c89a',foreground='#10251d',padding=(18,12))
 style.map('Play.TButton',background=[('active','#6bddad'),('disabled','#244c3f')],foreground=[('disabled','#829b90')])
 outer=tk.Frame(window,bg='#101b23',padx=28,pady=24);outer.pack(fill='both',expand=True)
 tk.Label(outer,text='MINECRAFT DUNGEONS II',font=('Segoe UI Semibold',10),fg='#61d0ab',bg='#101b23',anchor='w').pack(fill='x')
 tk.Label(outer,text=TITLE,font=('Segoe UI Semibold',22),fg='#f3f8fa',bg='#101b23',anchor='w').pack(fill='x',pady=(7,3))
 tk.Label(outer,text='Weapon damage estimates, right in your inventory.',font=('Segoe UI',11),fg='#acbdc7',bg='#101b23',anchor='w').pack(fill='x')
 card=tk.Frame(outer,bg='#1a2b35',padx=18,pady=16);card.pack(fill='x',pady=(23,19))
 badge=tk.StringVar(value='Finding your game…');location=tk.StringVar();status=tk.StringVar(value='Checking Steam libraries…')
 tk.Label(card,textvariable=badge,font=('Segoe UI Semibold',12),fg='#68d3ab',bg='#1a2b35',anchor='w').pack(fill='x')
 tk.Label(card,text='GAME FOLDER',font=('Segoe UI Semibold',8),fg='#8da8b8',bg='#1a2b35',anchor='w').pack(fill='x',pady=(13,4))
 entry=tk.Entry(card,textvariable=location,readonlybackground='#1a2b35',fg='#d8e5ec',font=('Segoe UI',10),relief='flat',state='readonly',borderwidth=0)
 entry.pack(fill='x')
 toolbar=tk.Frame(outer,bg='#101b23');toolbar.pack(fill='x')
 buttons=[];events=queue.Queue();cancel=threading.Event();busy=False;closed=False
 def busy_state(value):
  nonlocal busy
  busy=value
  for button in buttons:button.configure(state='disabled' if value else 'normal')
  cancel_button.configure(state='normal' if value else 'disabled')
 def run(task):
  if busy:return
  cancel.clear();busy_state(True)
  def execute():
   try:task()
   except Exception as error:events.put(('error',str(error)))
   finally:events.put(('done',''))
  threading.Thread(target=execute,daemon=True).start()
 def notify(text):events.put(('status',text))
 def refresh():
  try:
   path=find_game();events.put(('location',str(path)));events.put(('badge','Mod installed' if installed(path) else 'Ready to install'))
   notify('Press Install & Play. Setup is automatic.')
  except Exception as error:events.put(('badge','Choose your game folder'));notify(str(error))
 def choose():
  path=filedialog.askdirectory(parent=window,title='Choose your Minecraft Dungeons II folder')
  if not path:return
  try:
   path=normalize_game(path);save_location(path);location.set(str(path));badge.set('Mod installed' if installed(path) else 'Ready to install');status.set('Press Install & Play. Setup is automatic.')
  except Exception as error:messagebox.showerror(TITLE,str(error),parent=window)
 def play():
  selected=location.get()
  def task():
   path=normalize_game(selected);save_location(path)
   def progress(text):
    if text.startswith(('Mod installed.','Ready!')):events.put(('badge','Mod installed'))
    notify(text)
   install_and_play(path,progress,cancel)
   events.put(('badge','Mod installed'))
  run(task)
 def remove():
  selected=location.get()
  def task():
   path=normalize_game(selected);notify('Removing the mod…');count=remove_mod(path)
   events.put(('badge','Mod removed'));notify('Mod removed. Your other mods and saves are untouched.' if count else 'This mod is already removed.')
  run(task)
 play_button=ttk.Button(toolbar,text='Install & Play',style='Play.TButton',command=play);play_button.pack(side='left')
 remove_button=ttk.Button(toolbar,text='Remove mod',command=remove);remove_button.pack(side='left',padx=(10,0))
 cancel_button=ttk.Button(toolbar,text='Cancel',command=lambda:(cancel.set(),status.set('Stopped waiting. You can use the launcher again.')),state='disabled');cancel_button.pack(side='right')
 buttons.extend((play_button,remove_button))
 small=tk.Frame(outer,bg='#101b23');small.pack(fill='x',pady=(12,0))
 choose_button=ttk.Button(small,text='Choose folder…',command=choose);choose_button.pack(side='left')
 find_button=ttk.Button(small,text='Find automatically',command=lambda:run(refresh));find_button.pack(side='left',padx=(10,0));buttons.extend((choose_button,find_button))
 tk.Label(outer,textvariable=status,font=('Segoe UI',10),fg='#c6d7df',bg='#101b23',justify='left',anchor='nw',wraplength=590).pack(fill='x',pady=(16,0))
 tk.Label(outer,text='Close the game before removing the mod.',font=('Segoe UI',9),fg='#859da9',bg='#101b23',anchor='w').pack(fill='x',pady=(8,0))
 def drain():
  if closed:return
  while True:
   try:kind,value=events.get_nowait()
   except queue.Empty:break
   if kind=='location':location.set(value)
   elif kind=='badge':badge.set(value)
   elif kind=='status':status.set(value)
   elif kind=='error':status.set(value);messagebox.showerror(TITLE,value,parent=window)
   elif kind=='done':busy_state(False)
  window.after(100,drain)
 def close():
  nonlocal closed
  closed=True;cancel.set();window.destroy()
 window.protocol('WM_DELETE_WINDOW',close);window.after(100,drain);window.after(150,lambda:run(refresh));window.mainloop()
 return 0

if __name__=='__main__':sys.exit(main())
