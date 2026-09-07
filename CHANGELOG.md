# Changelog

## 1.1.0

- Add Personal Safety and Welcome Virtual Doorman icons, with launcher components verified on a connected device.
- Correct ChatGPT's source bounds so its visible mark measures 80 pixels across instead of 60 on the 192-pixel canvas.
- Restore the original Min application's launcher icon at all five source densities.
- Derive the output APK filename from the manifest version.

This is a minor release because it adds icon coverage without breaking compatibility. Android versionCode increases from 1 to 2; target SDK remains 37 and the signing key is unchanged.

## 1.0.0

- Preserve original Min artwork and add 32 app icons.
- Repair launcher component mappings and build a modern Android APK targeting API 37.
