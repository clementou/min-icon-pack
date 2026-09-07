# Min additions

The 34 icons added on top of the original Min pack. `scripts/build_apk.py` bundles these into the installable APK; see the [root README](../README.md).

To apply one without installing the pack, Nova can override icons individually: extract `min-additions.zip` on the phone, long-press an app shortcut, choose **Edit** (pencil), tap its icon, choose **Gallery apps**, and pick the matching PNG. Keep the whole square image including its transparent padding — Min relies on those margins to keep icons small.

Open `gallery.html` to compare the additions with official Play Store artwork and original Min icons. `preview.jpg` shows all 34 on a dark background.

## Sources and editable files

- `sources/`: downloaded publisher Play Store icons. The JSON files record the listing, verified listing title, and original image URL for each app.
- `svg/`: editable vectors traced from the publisher artwork, with a white face, a pale gray lower edge (normally 1.7 pixels; finer for detailed marks), and Min-sized transparent padding.
- `png/`: final transparent 192 × 192 PNGs.
- `traces/` and `masks/`: intermediate paths and source masks for rebuilding.
- `build-report.json`: provenance and validated visible bounds for each result.

The 1Password PNG is copied unchanged from Min itself. Its SVG is a traced silhouette for future editing, not a lossless representation of the original shading. Mini Metro is reconstructed from simple geometry, shortening the original full-bleed lines into a floating mark. Other icons use traced publisher artwork, not AI-generated images.

Monochrome adaptations necessarily remove the brand colors. Authenticator retains a pale gray person inside its white lock. TikTok keeps the white core of its mark. Stanford's shield uses white with transparent cutouts. Fine details and wordmarks may be harder to read at small launcher sizes; use the gallery to compare at your preferred display size.

## Rebuild

Run the scripts directly with uv. Each script declares its own pinned dependencies. The icon builder also requires Python 3.12 because vtracer crashes under Python 3.14; uv selects the compatible interpreter automatically.

```sh
uv run icons/fetch_sources.py
uv run icons/build.py
```

The fetcher caches existing downloads; only run it when sources are missing. The builder regenerates SVGs, PNGs, gallery, preview, and zip from saved sources. Make reproducible edits in `build.py`: direct SVG edits are overwritten. After artwork changes, run `uv run scripts/build_apk.py` to package and automatically verify them. Mapping-only changes do not need an artwork rebuild.

Reference for Nova's individual PNG workflow: https://www.androidcentral.com/how-make-custom-icon-android
