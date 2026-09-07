# Min Extended

An installable Android icon pack that continues [Min](https://play.google.com/store/apps/details?id=com.ryanmkelly.me.min), created in 2013 by [sixtyfour thirtytwo](https://www.sixtyfourthirtytwo.com/android.html) and no longer updated. It keeps all 1,547 original Min icons, adds 34 icons drawn in the same style, and repairs mappings for apps whose package or launcher activity has since changed.

Built and signed locally from the checked-in sources without Gradle. Python scripts use `uv run` with inline dependency metadata; uv manages Python and isolated dependencies automatically. The APK build runs offline once Python and the Android SDK are available.

## Install

Download the APK from [the latest release](https://github.com/clementou/min-icon-pack/releases/latest) and open it on the phone, or:

```sh
adb install -r min-extended-1.1.1.apk
```

To build it yourself instead:

```sh
uv run scripts/bootstrap_android.py     # one-time: fetch pinned Android SDK archives into .local/
uv run scripts/build_apk.py             # writes dist/min-extended-1.1.1.apk
adb install -r dist/min-extended-1.1.1.apk
```

The pack targets API 37, so it installs without `--bypass-low-target-sdk-block` — the flag the original 4.0.6.1 APK needs, since it still targets API 23. Its application ID is `io.github.clementou.miniconpack`, distinct from the original, so both packs can be installed side by side.

In Nova Launcher: **Settings → Look & feel → Icon style → Icon theme → Min Extended**.

[uv](https://docs.astral.sh/uv/guides/scripts/) and Java 17+ must be available. The build looks for `JAVA_HOME`, falling back to Homebrew's `openjdk`. No manual virtual environment setup is needed.

## New icons

1Password, Microsoft Authenticator, Beli, CBP MPC, ChatGPT, Chipotle, DoorDash, Dunkin, Fidelity, Google Fi, Google One, Grubhub, Google Health, Instacart, Lemonade, Mini Metro, Sutter Health My Health Online, Stanford Health Care MyHealth, Okta Verify, Oura, PagerDuty, ParkMobile, RENPHO Health, Roborock, Charles Schwab, Tesla, TikTok, Uber Eats, United Airlines, Waymo, Wealthfront, Zoom.

Version 1.1.0 adds Personal Safety and Welcome Virtual Doorman.

The icons use publisher Play Store artwork or editable vector designs restyled to match Min: a white face, a pale gray lower edge, and generous transparent padding on a 192 × 192 canvas. No generative images are used. `icons/preview.jpg` shows the full set on a dark background. See [`icons/README.md`](icons/README.md) to regenerate or edit them.

## Mappings

`android/mappings.json` holds 56 reviewed component fixes on top of the original `appfilter.xml`. The requested app mappings include 31 verified by querying launcher activities on a connected device; the rest cover package renames, activity aliases (Google Health launches through `com.fitbit.HealthBrandedAlias`, for instance), and three apps that were not installed and were cross-checked against the Delta Icons appfilter.

Edit `android/mappings.json` directly, then run `uv run scripts/build_apk.py`. The build validates schema, duplicates, drawable existence, and new-app mapping coverage, and automatically verifies compiled artwork and mappings. Actual launcher activities still need device or manifest verification: a valid-looking typo cannot be detected offline.

For artwork changes, run `uv run icons/build.py` first. Source fetching and SDK bootstrap are only needed when inputs are missing. `scripts/verify_assets.py` is called automatically by the build; it can also verify an existing APK independently. The obsolete audit and migration scripts have been removed.

The repository skill [min-icon-pack](.agents/skills/min-icon-pack/SKILL.md) is the agent handoff guide for adding icons, checking components, matching the style, and releasing. Script comments explain implementation details.

## Layout

- `original/Min-4.0.6.1.apk` — the last published Min release (`com.ryanmkelly.me.min`), preserved unchanged.
- `original/icons/` — 1,547 extracted 192 × 192 PNG resources.
- `original/assets/` — the original `appfilter.xml`, `drawable.xml`, and theme configs.
- `icons/` — the 34 additions: sources, vectors, PNGs, and their build.
- `android/` — `AndroidManifest.xml`, `MainActivity.java`, and the mapping fixes.
- `scripts/` — SDK bootstrap, APK build, and automatic asset verification.
- `dist/` — build output (ignored).

## Style notes

Min was made to let the wallpaper show through — minimal shadows on a white base. Its icons are white or near-white symbols on transparent canvases with a lot of empty space; the visible mark is much smaller than the canvas. Shapes are simplified with rounded details and restrained pale gray shading that reads as a slight fold. It is not a strictly flat style, and the symbol is never scaled to fill the canvas. When adding icons, compare visible size, stroke weight, and shading against several originals on both light and dark backgrounds.

Monochrome adaptation necessarily drops brand color. Fine details and wordmarks are harder to read at launcher size — check `icons/gallery.html` at your preferred display size before committing to one.

## Credit

Min was designed by [sixtyfour thirtytwo](https://www.sixtyfourthirtytwo.com/android.html), a graphic designer who spent four years on Android iconography — nine icon packs, two wallpaper collections, and over 12,000 icons, with more than a million downloads. Min itself launched in 2013 and passed 500,000 downloads. Their other work, including Tendere, Cast, Orbis, Hexacon, and Redux, is [on the Play Store](https://play.google.com/store/apps/dev?id=8299733615364824380).

All original artwork in `original/` is theirs. This repository is an unofficial continuation for personal use, not affiliated with or endorsed by the original author.
