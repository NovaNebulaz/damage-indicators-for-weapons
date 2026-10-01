# Damage Indicators for weapons



Weapon damage estimates in the Minecraft Dungeons II inventory, with your current loadout's boosts included.



**[Download the launcher](https://github.com/NovaNebulaz/damage-indicators-for-weapons/releases/latest)** Â· **[Installation](docs/INSTALL.md)** Â· **[Game editions](docs/COMPATIBILITY.md)** Â· **[Troubleshooting](docs/TROUBLESHOOTING.md)**



## Get started



1. Open the latest release and download **Damage Indicators for weapons.exe**, or download the portable ZIP and extract it first.

2. Keep the launcher wherever you like. It does not belong in the game's folder.

3. Close the game for the first installation. Open the launcher and press **Install & Play**.

4. Open your character and inventory. The launcher waits for the game to load and enables the weapon display.



No Python installation or separate mod loader is needed for the EXE.



## What it shows



- Melee hit ranges with the selected weapon's power and your current boosts.

- Quick and fully charged ranged hits.

- Separate critical and full-health hit estimates where applicable.

- Normal effect descriptions on armor, talismans, and other non-weapon items.



Numbers assume a neutral target. Enemy defenses, distance, partial charge, and special effects can change the damage you deal. An unequipped weapon uses your current loadout's boosts; the mod does not simulate replacing every enchantment and effect in your build.



## Supported editions



| Edition | This release |

| --- | --- |

| Minecraft Dungeons II, Steam on Windows 10/11 x64 | Supported for the verified executable listed in [Compatibility](docs/COMPATIBILITY.md) |

| Minecraft Launcher / Minecraft.net purchase | Not supported by this Steam adapter |

| Microsoft Store / Xbox app / PC Game Pass | Not supported by this Steam adapter |

| Original Minecraft Dungeons, consoles, cloud streaming | Not supported |



Choosing another folder does not add support for another game build. The launcher checks the executable before installing anything.



## Remove it



Close the game, open the launcher, and press **Remove mod**. It removes this mod, restores files it replaced, and leaves other mods and saves alone. Afterwards, you can delete the launcher folder.



## Manual install and source downloads



The [manual guide](docs/INSTALL.md#manual-installation-steam) lists the exact folder and all three files to copy. Manual installation still needs the launcher to start the temporary damage worker each session.



GitHub's **Code > Download ZIP** downloads the source project. For a ready-to-run EXE, use **Releases** instead. The release ZIP includes the launcher, source, mod files, and instructions.



## Project layout



```text

source/                 Launcher and damage worker

source/assets/          Mod containers, native formatter, and icon

source/native/          Formatter assembly and rebuild tool

docs/                   Installation, compatibility, and troubleshooting

tests/                  Installation and startup tests

tools/                  Release packaging

.github/workflows/      Windows build and release workflow

licenses/               Bundled runtime notices

```



[Build from source](docs/BUILD.md) Â· [Changelog](CHANGELOG.md) Â· [Report a problem](https://github.com/NovaNebulaz/damage-indicators-for-weapons/issues)



The launcher code is MIT licensed. See [LICENSE](LICENSE) and [third-party notices](docs/THIRD_PARTY.md). Unofficial mod; not affiliated with Mojang or Microsoft.



### Weapon speed



Weapon tooltips also show **Speed: 1–10**, including your current attack-speed boosts. Higher means faster within the same weapon category. See [compatibility and calculation details](docs/COMPATIBILITY.md#weapon-speed).

