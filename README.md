# Min Extended

An installable Android icon pack that continues [Min](https://play.google.com/store/apps/details?id=com.dkkim.min) after its author stopped updating it. It keeps all 1,547 original Min icons, adds 32 icons drawn in the same style for apps that shipped after the last release, and repairs mappings for apps whose package or launcher activity has since changed.

Built and signed locally from the checked-in sources: no Gradle, no network access at build time.

## Install

```sh
python3 scripts/bootstrap_android.py     # one-time: fetch pinned Android SDK archives into .local/
python3 scripts/build_apk.py             # writes dist/min-extended-1.0.0.apk
adb install dist/min-extended-1.0.0.apk
```

The pack targets API 36, so it installs without `--bypass-low-target-sdk-block` — the flag the original 4.0.6.1 APK needs on current Android. Its application ID is `io.github.clementou.miniconpack`, distinct from the original, so both packs can be installed side by side.

In Nova Launcher: **Settings → Look & feel → Icon style → Icon theme → Min Extended**.

Java 17+ must be available. The build looks for `JAVA_HOME`, falling back to Homebrew's `openjdk`.

## New icons

1Password, Microsoft Authenticator, Beli, CBP MPC, ChatGPT, Chipotle, DoorDash, Dunkin, Fidelity, Google Fi, Google One, Grubhub, Google Health, Instacart, Lemonade, Mini Metro, Sutter Health My Health Online, Stanford Health Care MyHealth, Okta Verify, Oura, PagerDuty, ParkMobile, RENPHO Health, Roborock, Charles Schwab, Tesla, TikTok, Uber Eats, United Airlines, Waymo, Wealthfront, Zoom.

Each is traced from publisher Play Store artwork and restyled to match Min: a white face, a pale gray lower edge, and generous transparent padding on a 192 × 192 canvas. No generative images are used. `icons/preview.jpg` shows the full set on a dark background. See [`icons/README.md`](icons/README.md) to regenerate or edit them.

## Mappings

`android/mappings.json` holds 54 reviewed component fixes on top of the original `appfilter.xml`. Twenty-nine were verified by querying launcher activities on a connected device; the rest cover package renames, activity aliases (Google Health launches through `com.fitbit.HealthBrandedAlias`, for instance), and three apps that were not installed and were cross-checked against the Delta Icons appfilter.

`scripts/audit_mappings.py` re-runs that audit against whatever is installed on an attached device and proposes repairs. Inventory it produces stays in ignored `.local/`.

## Layout

- `original/Min-4.0.6.1.apk` — the last published Min release, preserved unchanged.
- `original/icons/` — 1,547 extracted 192 × 192 PNG resources.
- `original/assets/` — the original `appfilter.xml`, `drawable.xml`, and theme configs.
- `icons/` — the 32 additions: sources, vectors, PNGs, and their build.
- `android/` — `AndroidManifest.xml`, `MainActivity.java`, and the mapping fixes.
- `scripts/` — SDK bootstrap, APK build, and the mapping audit.
- `dist/` — build output (ignored).

## Style notes

Min's icons are white or near-white symbols on transparent canvases with a lot of empty space; the visible mark is much smaller than the canvas. Shapes are simplified with rounded details and restrained pale gray shading that reads as a slight fold. It is not a strictly flat style, and the symbol is never scaled to fill the canvas. When adding icons, compare visible size, stroke weight, and shading against several originals on both light and dark backgrounds.

Monochrome adaptation necessarily drops brand color. Fine details and wordmarks are harder to read at launcher size — check `icons/gallery.html` at your preferred display size before committing to one.

## Credit

Original artwork by the Min author. This repository is an unofficial continuation for personal use.
