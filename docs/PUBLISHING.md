# Repository setup

Suggested repository name: `damage-indicators-for-weapons`.

Description: `Inventory weapon damage estimates and a portable mod launcher for Minecraft Dungeons II.`

Suggested topics: `minecraft-dungeons-ii`, `minecraft-dungeons`, `mod`, `windows`, `launcher`.

## Source files

Commit the project files, including the small mod payloads in `source/assets`. Keep compiled EXEs and release ZIPs out of Git history; publish them as release assets instead. Do not upload local adapter-session files, game files, saves, or installation backups.

## Automatic release

With `.github/workflows/release.yml` committed, the first push to `main` builds and publishes version 1.0.0. Check **Actions → Windows release** for progress, then open **Releases** to verify all three assets are present.

If Actions is disabled, enable the workflow for this repository or use the manual release steps below. If your GitHub connection cannot upload workflow files, add `release.yml` through your normal Git workflow first.

## Manual release

1. Build with the commands in [Build](BUILD.md), or use the prepared files in `release-assets` from the local handoff package.
2. Open **Releases → Draft a new release**.
3. Create tag `v1.0.0`, targeting `main`.
4. Title it **Damage Indicators for weapons v1.0.0**.
5. Copy the description from [Release notes](RELEASE_NOTES.md).
6. Attach the EXE, portable ZIP, and `SHA256.txt` from `dist` or `release-assets`.
7. Publish the release and mark it as latest.

GitHub automatically adds source-code archives. Those are different from the portable ZIP you attach.

If moving the repository to another owner or changing its name, update the download and issue links in the root README.
