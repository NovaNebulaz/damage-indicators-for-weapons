# Game editions and updates

This mod is for **Minecraft Dungeons II**, not the original Minecraft Dungeons.

## Verified Steam build

- Windows 10/11, x64.
- Steam app ID: `1912410`.
- Executable: `Dungeons\Binaries\Win64\Dungeons-Win64-Shipping.exe`.
- Tested locally on September 30 and October 1, 2026.
- Supported executable SHA-256 values:

```text
7c83afbf0ad34a40b853cdb25a22fffb605d08e2a1e2d431974d7c7c1ee0ba54
231147bd0c655a4ae73f90873675d42917f2bfb3a9ee164fc64f217d6d6bd4ef
```

Steam editions with different DLC purchases are not separate supported builds by themselves. What matters is the executable and runtime layout. The launcher verifies the executable hash before installation and checks the live tooltip and player-stat layouts before enabling estimates.

## Other PC editions

**Minecraft Launcher / Minecraft.net webstore:** buying from the website does not establish compatibility with this Steam executable. Check the actual installed edition and use its normal launcher. This release's Install & Play button starts Steam, so it is not a launcher for the webstore edition.

**Microsoft Store / Xbox app / PC Game Pass:** the official [Xbox game page](https://www.xbox.com/en-us/games/minecraft-dungeons-ii) lists Windows support. Availability on Windows does not mean the Steam mod's executable addresses, package layout, or startup method are the same. Those builds have not been inspected or tested for this release.

**Console and cloud streaming:** this Windows launcher cannot install a mod into a console or remote cloud game.

There are no verified instructions for installing this release on the non-Steam PC editions. Do not change the accepted hash to force installation, copy Steam executable files into another edition, or change protected-folder permissions to make the installer proceed.

## Adding another edition or game update

A supported port needs more than a new install path:

1. Identify the local executable, normal launch method, and writable mod directory for that edition.
2. Verify that the widget containers load correctly in that build.
3. Inspect the tooltip handler, object/name tables, player attributes, and weapon-definition layouts.
4. Rebuild the formatter's native function references and validate its calling conventions.
5. Check ordinary melee, quick-shot, charged-shot, critical, and full-health estimates against that build's damage calculation.
6. Test startup, inventory navigation, loadout changes, game exit, installation, and removal.
7. Add that edition as a separate verified adapter and document its executable hash.

The current Steam references are in `source/inventory_estimates.py` and `source/live_game_stats.py`. The formatter is under `source/native`, and the ordinary-hit model is in `source/combat_model.py`.

To request a port, open an issue with the edition, visible game version, Windows version, and the exact message you received. Do not upload the game executable, saves, account information, or a full game archive.

## Weapon speed

Speed runs from 1 (slow) to 10 (fast), compared within melee or ranged weapons. Melee uses the complete combo animation duration, number of hit events, animation rate, variant speed multipliers and cooldowns. Ranged uses its firing interval, plus charge time where charging is required. Your current melee or ranged attack-speed boost affects the rating.

This is a nominal timing estimate, not measured attacks per second. Multi-hit combo steps count as multiple strikes. Animation cancelling, recovery windows, movement, volleys and charge choices can change actual cadence. A melee 10 and a ranged 10 are not the same firing rate. Damage estimates still describe a neutral target, with conditional critical and full-health damage listed separately.
