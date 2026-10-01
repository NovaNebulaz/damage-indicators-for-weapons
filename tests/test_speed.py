import pathlib,sys,unittest,math
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'source'))
from weapon_data import speed_rating,melee_period,TIMING
class SpeedTests(unittest.TestCase):
 def test_endpoints(self):
  self.assertEqual(speed_rating(2,2,.5),1)
  self.assertEqual(speed_rating(.5,2,.5),10)
 def test_faster_attacks_and_boosts(self):
  self.assertGreater(speed_rating(.75,2,.5),speed_rating(1.5,2,.5))
  self.assertGreater(speed_rating(1,2,.5,1.5),speed_rating(1,2,.5))
 def test_clamps_and_invalid_data(self):
  self.assertEqual(speed_rating(.1,2,.5),10)
  self.assertEqual(speed_rating(5,2,.5),1)
  for period in (0,-1,float('nan'),float('inf')):self.assertEqual(speed_rating(period,2,.5),0)

 def test_claws_multi_hits_are_faster_than_great_axe(self):
  axe=melee_period(TIMING['AM_Player_GreatAxeCombo_Unique1'],[1,1],[0,0])
  claws=melee_period(TIMING['AM_Player_ClawsCombo_Unique1'],[1.4,1.5,1.5],[0,0,0])
  self.assertLess(claws,axe/2)
  self.assertGreater(speed_rating(claws,1.92,.40),speed_rating(axe,1.92,.40))
 def test_multi_hits_and_short_spear_sections(self):
  t=TIMING['AM_Player_ShortSpearCombo']
  self.assertGreater(melee_period(t,[1.4,1.75,1.5],[0,0,0]),0)
  single=dict(t,hits=1)
  self.assertAlmostEqual(melee_period(single,[1.4,1.75,1.5],[0,0,0]),4*melee_period(t,[1.4,1.75,1.5],[0,0,0]))
