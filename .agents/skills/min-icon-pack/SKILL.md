---
name: min-icon-pack
description: Add or refine Min Extended icons, repair Android launcher mappings, and build this repository's APK for Nova Launcher.
---

# Min icon pack

Run commands from the repository root. Read `icons/README.md` for artwork inputs and `README.md` for installation. Use `uv run`; dependencies and Python requirements are declared inline, with no manual virtualenv.

## Mapping-only changes

Edit `android/mappings.json` directly. It is the authoritative override list, not output to regenerate from a device inventory. Each entry has exactly these fields:

```json
{"component":"com.openai.chatgpt/com.openai.chatgpt.MainActivity","drawable":"min_chatgpt","source":"device launcher query"}
```

Confirm the actual component rather than guessing:

```sh
adb shell cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -p com.openai.chatgpt
```

Replace the package for the target app. Expand returned `.Activity` names to `package.Activity`; omit `ComponentInfo{}` wrappers. Include relevant launcher aliases. Activity namespaces may differ from package namespaces. Play Store listing IDs verify packages, not activities. For absent apps, inspect the APK manifest or corroborate a maintained public appfilter and record its URL. Full device inventories belong in ignored `.local/`.

New resource names are `min_` plus the `icons/apps.json` ID with hyphens replaced by underscores. Original resources use the filename stem under `original/icons/`. Distinct components can share a drawable, but duplicate components are errors.

Run `uv run scripts/build_apk.py`. The build validates schema, duplicates, resource existence, new-app drawable assignments and mapping coverage, then verifies compiled artwork, reviewed mappings, signing and alignment. It cannot detect a syntactically valid but nonexistent activity offline; verify provenance first.

## Artwork changes

1. For a new app, add a unique lowercase hyphenated `id`, display `name`, and verified `package` to `icons/apps.json`, and add its launcher mapping.
2. Run `uv run icons/fetch_sources.py` if source artwork is missing. It downloads official Play Store artwork and records provenance in `icons/sources/`. Inspect the image and listing title. Existing downloads are cached: refreshing requires explicitly replacing the relevant source image and metadata.
3. Modify extraction rules or custom vector geometry in `icons/build.py`. SVGs and PNGs are generated outputs; direct SVG edits are overwritten. Use official vectors or deterministic masks traced from publisher artwork, not generative images.
4. Run `uv run icons/build.py`, inspect changed PNGs and `icons/preview.jpg`/`icons/gallery.html`, then run `uv run scripts/build_apk.py`.

Match several original Min icons: transparent 192×192 canvas, typically an approximately 80-pixel visible mark, white-to-#f6f6f6 face and restrained #dcdcdc lower edge (normally 1.7 pixels, less for fine marks). Judge optical size and stroke weight at launcher size on light and dark backgrounds. Corner pixels and trademarks can distort source mask bounds; this previously made ChatGPT too small. Keep Uber Eats lines equally weighted and TikTok's silhouette crisp. Mini Metro uses custom route/station geometry. The 1Password PNG intentionally preserves the original pixels.

The icon builder requires Python 3.12 because vtracer crashes on 3.14; uv selects it. CairoSVG also requires a system Cairo library. Expand the fixed contact-sheet grids in both artwork scripts when additions exceed their capacity.

## Setup and release

Only without an existing SDK: `uv run scripts/bootstrap_android.py`. Java 17+ is required; set `JAVA_HOME` if the Homebrew default does not apply. `ANDROID_SDK_ROOT` can select another SDK.

For a requested release, update `android/AndroidManifest.xml` versionName using SemVer (new icons: minor; artwork/mapping corrections: patch; incompatible changes: major), increment versionCode, and update `CHANGELOG.md`. Preserve the application ID, modern target SDK and original pack launcher artwork. Output is `dist/min-extended-VERSION.apk` with checksum and report.

Preserve `.local/signing/min-release.jks` and its password: updates require the same key. A fresh clone without these generates a different key. Never commit signing material or device inventories. Track source artwork/provenance, generator changes, generated SVG/PNG/preview, mappings and release metadata as applicable; build outputs and intermediates are ignored. When installation is requested, use `adb install -r dist/min-extended-VERSION.apk` and select Min Extended in Nova. A documentation or mapping review does not itself call for installing or publishing.

When changing validation/build code, run `uv run --with pillow==12.3.0 python -m unittest discover -s tests` and a real APK build.
