# Build from source

Use 64-bit Windows and Python 3.12 with Tkinter. Runtime users do not need Python; these steps are for building or editing the launcher.

From the project folder:

```powershell
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
python source/build.py
python tools/package_release.py
```

The launcher EXE appears in the project folder. `dist` contains the EXE, portable ZIP, and `SHA256.txt` ready for a GitHub release. The game itself is not needed for the fixture tests or the build.

The EXE bundles `source/assets`, so it can be moved out of the source project. Keep the runtime notices in distributed ZIP packages.

## Native formatter

The verified formatter is already included as `source/assets/estimate_hook.bin`; normal launcher builds do not need to assemble it again.

To regenerate it, install `keystone-engine==0.9.2`, then run `python source/native/build_formatter.py`. This also writes the assembly listing and patch metadata. Changing the formatter or game references requires another round of live-game checks; a successful build alone does not establish compatibility.

## GitHub releases

The Windows release workflow runs when `main` changes, when a version tag is pushed, or when manually started from **Actions → Windows release → Run workflow**. It builds and tests on Windows, then publishes the release downloads for the version in `source/version.txt`.

An existing release version is left unchanged. For a new release, update the numeric product and file versions in `source/version.txt`, the changelog, and release notes first. If using a tag, it must match the product version, such as `v1.0.0`.

See [Publishing](PUBLISHING.md) for repository setup and manual release uploads.
