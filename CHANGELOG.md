# Changelog

## 1.1.1

- Restore the original Min-style dark rim and downward shadow on all 33 newly drawn icons, improving contrast on white backgrounds.
- Generate shadows automatically in the artwork pipeline; preserve the original 1Password PNG unchanged.
- Add a white-background preview and document reproducible shadow rendering.

This is a patch release correcting existing artwork. Android versionCode increases to 3; target SDK, application ID, mappings, and signing key are unchanged.

## 1.1.0

- Add Personal Safety and Welcome Virtual Doorman icons, with launcher components verified on a connected device.
- Correct ChatGPT's source bounds so its visible mark measures 80 pixels across instead of 60 on the 192-pixel canvas.
- Restore the original Min application's launcher icon at all five source densities.
- Derive the output APK filename from the manifest version.

This is a minor release because it adds icon coverage without breaking compatibility. Android versionCode increases from 1 to 2; target SDK remains 37 and the signing key is unchanged.

## 1.0.0

- Preserve original Min artwork and add 32 app icons.
- Repair launcher component mappings and build a modern Android APK targeting API 37.
