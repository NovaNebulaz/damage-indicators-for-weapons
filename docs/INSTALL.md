# Installation

## Download

Open the repository's **Releases** page and expand **Assets**.

| Download | Use it for |
| --- | --- |
| `Damage Indicators for weapons.exe` | The launcher by itself; runtime and mod files are bundled inside |
| `Damage Indicators for weapons.zip` | The launcher plus source, mod files, and documentation |
| `SHA256.txt` | Checking release download hashes |
| GitHub's `Source code (zip)` or `Code → Download ZIP` | Building or editing the project; no prebuilt EXE |

Extract a ZIP with **Extract All** before running anything. Keep the launcher in a normal folder such as Documents or a games-tools folder. Do not put it into `Binaries`, `Paks`, or `~mods`.

## Automatic installation — Steam

1. Exit Minecraft Dungeons II normally.
2. Open **Damage Indicators for weapons.exe**.
3. Check the game folder it found. Steam libraries on other drives are supported.
4. If needed, press **Choose folder** and select the Minecraft Dungeons II installation containing the `Dungeons` folder.
5. Press **Install & Play**. The mod installs and Steam opens the game.
6. Open your character and inventory. Wait for **Ready! Damage estimates are enabled in inventory.**

Use this launcher whenever you want the estimates. Launching through Steam alone does not start the temporary damage worker. The launcher window can be closed once it says Ready; the worker continues until the game exits.

## Manual installation — Steam

First check [Compatibility](COMPATIBILITY.md). These instructions apply to the verified Steam build.

1. Close the game.
2. In Steam, right-click **Minecraft Dungeons II → Manage → Browse local files**.
3. From that installation folder, open `Dungeons\Content\Paks`.
4. Create a folder named `~mods` if it does not exist.
5. Copy these three files from this project's `source\assets` into `~mods`:

```text
zzz_DamageIndicatorsForWeapons_P.pak
zzz_DamageIndicatorsForWeapons_P.ucas
zzz_DamageIndicatorsForWeapons_P.utoc
```

All three files must remain together with their original names. Copying only the `.pak` is not enough.

For the default Steam library, the destination is:

```text
C:\Program Files (x86)\Steam\steamapps\common\Minecraft Dungeons II\Dungeons\Content\Paks\~mods\
```

For a Steam library on another drive, it could be:

```text
D:\SteamLibrary\steamapps\common\Minecraft Dungeons II\Dungeons\Content\Paks\~mods\
```

The installed files should look like this:

```text
Minecraft Dungeons II/
└── Dungeons/
    └── Content/
        └── Paks/
            └── ~mods/
                ├── zzz_DamageIndicatorsForWeapons_P.pak
                ├── zzz_DamageIndicatorsForWeapons_P.ucas
                └── zzz_DamageIndicatorsForWeapons_P.utoc
```

Keep the EXE outside that folder and press **Install & Play**. It recognizes the files already installed and starts the damage worker. The containers supply the inventory widget; the worker supplies the estimates. Copying the containers without starting the worker is not a complete installation.

Do not replace the game's executable or `PrecompiledScript.Cache`. Do not copy the source scripts into the game's script folder.

## Minecraft Launcher, webstore, and Microsoft Store purchases

See [Game editions](COMPATIBILITY.md#other-pc-editions). This release does not include an adapter for those installations. There is no verified manual installation procedure for them yet; using their folder with this Steam release will not make the damage worker compatible.

## Uninstall

**Launcher:** close the game and press **Remove mod**. Files modified outside the launcher are left alone, with an explanation if removal cannot proceed.

**Manual:** close the game and remove only the three `zzz_DamageIndicatorsForWeapons_P` files listed above. Keep every other file in `~mods`. If you backed up existing files before copying, restore your backups. Delete the launcher when finished.

Settings and installation backups are stored in `%LOCALAPPDATA%\DamageIndicatorsForWeapons`. Keep backups until removal is finished. The launcher does not change saves or combat values.
