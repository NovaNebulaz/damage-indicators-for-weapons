"""Exercise discovery, installation, migration, removal and rollback in fixtures."""
import importlib,pathlib,sys,tempfile,json,unittest,threading
from unittest.mock import patch
source=pathlib.Path(__file__).resolve().parents[1]/'source';sys.path.insert(0,str(source))
import mod_manager as m

class LauncherTests(unittest.TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.directory.name)
  self.game=self.root/'library/steamapps/common/Installed Game';exe=self.game/m.EXE;exe.parent.mkdir(parents=True);exe.write_bytes(b'tested executable')
  self.state=patch.object(m,'STATE',self.root/'state');self.state.start()
  self.expected=patch.object(m,'EXPECTED',m.digest(exe));self.expected.start()
  self.process=patch.object(m,'game',return_value=None);self.active=self.process.start()
  self.mods=m.mod_folder(self.game);self.mods.mkdir(parents=True)
  self.unrelated=self.mods/'KeepThisOtherMod.pak';self.unrelated.write_bytes(b'unrelated mod')
 def tearDown(self):self.process.stop();self.expected.stop();self.state.stop();self.directory.cleanup()
 def test_install_and_remove_preserve_other_mods_and_originals(self):
  collision=self.mods/(m.STEM+'.pak');collision.write_bytes(b'previous user file')
  self.assertTrue(m.install_mod(self.game));self.assertTrue(m.installed(self.game))
  self.active.return_value={'pid':123};self.assertFalse(m.install_mod(self.game))
  with self.assertRaisesRegex(ValueError,'Close Minecraft'):m.remove_mod(self.game)
  self.active.return_value=None;self.assertEqual(m.remove_mod(self.game),3)
  self.assertEqual(collision.read_bytes(),b'previous user file');self.assertEqual(self.unrelated.read_bytes(),b'unrelated mod')
  self.assertFalse((self.mods/(m.STEM+'.ucas')).exists())
 def test_legacy_migration(self):
  fixture=self.root/'assets';m.shutil.copytree(m.ASSETS,fixture)
  hashes={}
  for ext in m.EXTENSIONS:
   old=self.mods/('OldWeaponMod.'+ext);old.write_bytes(('previous '+ext).encode());hashes[ext]=m.digest(old)
  (fixture/'legacy-hashes.json').write_text(json.dumps(hashes))
  replacement=patch.object(m,'ASSETS',fixture);replacement.start();self.addCleanup(replacement.stop)
  self.assertEqual(len(m.legacy_files(self.game)),3);m.install_mod(self.game)
  self.assertFalse(list(self.mods.glob('OldWeaponMod.*')));m.remove_mod(self.game)
  self.assertEqual(list(self.mods.iterdir()),[self.unrelated])
 def test_running_game_blocks_initial_install(self):
  self.active.return_value={'pid':123}
  with self.assertRaisesRegex(ValueError,'Close Minecraft'):m.install_mod(self.game)
  self.assertEqual(list(self.mods.iterdir()),[self.unrelated])
 def test_game_update_does_not_write_files(self):
  (self.game/m.EXE).write_bytes(b'changed game')
  with self.assertRaisesRegex(ValueError,'not supported'):m.install_mod(self.game)
  self.assertEqual(list(self.mods.iterdir()),[self.unrelated])
 def test_external_mod_change_is_not_removed(self):
  m.install_mod(self.game);changed=self.mods/(m.STEM+'.utoc');changed.write_bytes(b'custom change')
  snapshot={p.name:p.read_bytes() for p in self.mods.iterdir()}
  with self.assertRaisesRegex(ValueError,'changed outside'):m.remove_mod(self.game)
  self.assertEqual(snapshot,{p.name:p.read_bytes() for p in self.mods.iterdir()})
 def test_failed_copy_rolls_back(self):
  original=m.shutil.copyfile;calls=0
  def copy(src,dst):
   nonlocal calls
   calls+=1
   if calls==2:raise OSError('simulated copy failure')
   return original(src,dst)
  with patch.object(m.shutil,'copyfile',side_effect=copy):
   with self.assertRaisesRegex(OSError,'simulated'):m.install_mod(self.game)
  self.assertEqual(list(self.mods.iterdir()),[self.unrelated]);self.assertFalse(m.installed(self.game))
 def test_steam_secondary_library_and_escaped_paths(self):
  steam=self.root/'Steam';(steam/'steamapps').mkdir(parents=True)
  library=self.root/'library';path=str(library).replace('\\','\\\\')
  (steam/'steamapps/libraryfolders.vdf').write_text('"libraryfolders" { "0" { "path" "'+path+'" } }')
  (library/'steamapps/appmanifest_1912410.acf').write_text('"AppState" { "appid" "1912410" "installdir" "Installed Game" }')
  with patch.object(m,'steam_roots',return_value=[steam]):self.assertEqual(m.discover_games(),[self.game.resolve()])
  old='"LibraryFolders" { "1" "'+path+'" }'
  (steam/'steamapps/libraryfolders.vdf').write_text(old)
  with patch.object(m,'steam_roots',return_value=[steam]):self.assertEqual(m.discover_games(),[self.game.resolve()])
 def test_manual_folder_executable_and_parent_normalization(self):
  self.assertEqual(m.normalize_game(self.game/'Dungeons'),self.game.resolve())
  self.assertEqual(m.normalize_game(self.game/m.EXE),self.game.resolve())
 def test_initial_engine_loading_is_retried(self):
  m.install_mod(self.game)
  self.active.return_value={'pid':123,'path':str(self.game/m.EXE)}
  outcomes=iter([{'ok':False,'error':'Unsupported object layout.'},{'ok':True}])
  messages=[]
  def start(command,**kwargs):
   m.atomic_json(pathlib.Path(command[-1]),next(outcomes))
   class Child:
    def poll(self):return 0
   return Child()
  cancel=threading.Event()
  with patch.object(m.subprocess,'Popen',side_effect=start) as process,patch.object(cancel,'wait',return_value=False):
   m.install_and_play(self.game,messages.append,cancel)
  self.assertEqual(process.call_count,2)
  self.assertIn('Mod installed. Waiting for the game…',messages)
  self.assertEqual(messages[-1],'Ready! Damage estimates are enabled in inventory.')
 def test_changed_runtime_layout_is_still_rejected(self):
  m.install_mod(self.game)
  self.active.return_value={'pid':123,'path':str(self.game/m.EXE)}
  def start(command,**kwargs):
   m.atomic_json(pathlib.Path(command[-1]),{'ok':False,'error':'The font layout changed.'})
   class Child:
    def poll(self):return 0
   return Child()
  with patch.object(m.subprocess,'Popen',side_effect=start):
   with self.assertRaisesRegex(RuntimeError,'font layout changed'):
    m.install_and_play(self.game,lambda _:None,threading.Event())

if __name__=='__main__':unittest.main(verbosity=2)
