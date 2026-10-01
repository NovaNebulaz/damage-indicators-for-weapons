# Source

Run `python launcher.py` on Windows with Python 3.11 or later and Tkinter available. The executable includes its own runtime, so normal users do not need Python.

`mod_manager.py` finds Steam libraries, checks the tested game build, installs/removes the three mod container files and starts the game through Steam. `inventory_estimates.py` installs the temporary inventory handler; `live_game_stats.py` and `weapon_data.py` read the verified game layouts. `combat_model.py` documents the recovered ordinary-hit arithmetic. Native formatter data and the rebuilt tooltip widget are under `assets`.

Removal checks file ownership and hashes. It restores backed-up files that setup replaced and leaves modified or unrelated files alone. The worker stops when the game exits. No combat values or saves are modified.

To rebuild on 64-bit Windows, install `pyinstaller==6.22.3` with Python 3.12, then run `python build.py`. Keep `assets` alongside the source. The resulting executable bundles its own runtime and assets. Retain the third-party notices when distributing it.
