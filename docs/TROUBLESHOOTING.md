# Troubleshooting

### The game is not found

Press **Find automatically**. If that fails, use **Choose folder** and select the Minecraft Dungeons II installation that contains `Dungeons`. Steam's **Manage → Browse local files** opens the right folder.

### The launcher is waiting for inventory

Finish loading your character and open inventory. Startup can take a while; the launcher retries while the game's player data becomes available. It stops waiting after five minutes. Press Install & Play again if your loading session took longer.

### “Unsupported object layout” appears during startup

The first release includes a retry for this loading-screen condition. Use the latest launcher and close any older launcher window. If it still appears after your character is loaded, report the game build and edition.

### “This game update is not supported yet”

The executable differs from the verified build. No installation is performed. Check [Compatibility](COMPATIBILITY.md) and wait for an adapter verified against that update. Renaming files or changing the hash does not fix the runtime references.

### Steam error 0042

Start Steam and sign in, then use Install & Play. Avoid launching the game's shipping executable directly. The mod does not provide a replacement for the game's normal sign-in.

### There are no estimates after a manual install

All three container files must be in `Dungeons\Content\Paks\~mods`. Start the EXE and press Install & Play each session; the temporary worker is also required.

### Some damage differs from a hit in combat

The display assumes a neutral target and your current loadout's boosts. Resistance, charge amount, distance, special effects, and conditional boosts can change a real hit. Critical and full-health lines are separate conditions, not guaranteed damage on every attack.

### A file cannot be written

Close the game and check that the folder belongs to the correct installation and is writable. Do not change Windows security settings or protected-folder ownership. If the selected game is a Store installation, it is not supported by this release.

### Removal says a mod file was changed

The launcher refuses to delete a file that no longer matches its installed copy. Keep a copy of your changed file and investigate before removing it manually. Unrelated mods are never part of this mod's removal list.

### Reporting a problem

Include the launcher version, game edition, visible game version, exact error, and the steps that caused it. A cropped screenshot of the affected tooltip helps with display problems. Review anything you share for account names and personal paths first.
