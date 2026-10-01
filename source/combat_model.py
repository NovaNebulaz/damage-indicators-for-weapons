"""Damage arithmetic recovered from the tested game's native hit routine."""
import math

DAMAGE_ATTRIBUTES=('MeleeDamageMultiplier','RangedDamageMultiplier','FireDamageMultiplier',
 'IceDamageMultiplier','LightningDamageMultiplier','PoisonDamageMultiplier',
 'SoulDamageMultiplier','BlastDamageMultiplier','BlastDamageMultiplier')
RESISTANCE_ATTRIBUTES=('MeleeDamageResistanceMultiplier','RangedDamageResistanceMultiplier',
 'FireDamageResistanceMultiplier','IceDamageResistanceMultiplier','LightningDamageResistanceMultiplier',
 'PoisonDamageResistanceMultiplier','SoulDamageResistanceMultiplier','BlastDamageResistanceMultiplier',
 'TNTDamageResistanceMultiplier')
MODIFIER_ATTRIBUTES=('CriticalHitMultiplier','RangedChargedAttackMultiplier','RangedPointBlankAttackMultiplier',
 'MovementDamageMultiplier','OpportunityMultiplier','FullHealthTargetDamageMultiplier',
 'HurtTargetDamageMultiplier','PrimaryTargetDamageMultiplier','JumpingMeleeDamageMultiplier','ThrowableTntMultiplier')

def internal_hit(raw,stats,source,damage_flags,modifier_flags=0,resistance=None):
 """Ordinary non-percent damage, before shields and health loss are applied."""
 if raw<=0:return 0.0
 value=raw+stats['BaseDamageBonus']
 if source in ('Melee','Ranged'):
  value*=stats[source+'AttackWeaponMultiplier']*stats[source+'DamageSourceMultiplier']*stats['AttackEmpowerment']
  if modifier_flags&1:value*=stats['CriticalHitMultiplier'+source]
 elif source.startswith('Artifact'):
  value*=stats[source+'AttackWeaponMultiplier']*stats['ArtifactDamageMultiplier']
 value*=stats['BaseDamageMultiplier']
 for bit,name in enumerate(DAMAGE_ATTRIBUTES):
  if damage_flags&(1<<bit):value*=stats[name]
 for bit,name in enumerate(MODIFIER_ATTRIBUTES):
  if modifier_flags&(1<<bit):value*=stats[name]
 if damage_flags&252:value*=stats['ElementalDamageMultiplier']
 if resistance:
  value*=resistance['BaseDamageResistanceMultiplier']*resistance['ArmorMultiplier']
  for bit,name in enumerate(RESISTANCE_ATTRIBUTES):
   if damage_flags&(1<<bit):value*=resistance[name]
  if damage_flags&252:value*=resistance['ElementalDamageResistanceMultiplier']
 return max(0.0,value)

def display_factor(power,fudge):
 if not math.isfinite(power) or not 1<=power<1000 or not 0<=fudge<=1:raise ValueError('Unsupported item power or display scaling.')
 return 1+(power-1)*fudge

def weapon_hit(raw,stats,kind,power,fudge,modifiers=128):
 """Primary-target number against a neutral enemy, in floating-hit-number units."""
 weapon_multiplier=stats[kind+'AttackWeaponMultiplier']
 if not math.isfinite(weapon_multiplier) or weapon_multiplier<=0:raise ValueError('Weapon scaling unavailable.')
 return internal_hit(raw,stats,kind,1 if kind=='Melee' else 2,modifiers)*display_factor(power,fudge)/weapon_multiplier
