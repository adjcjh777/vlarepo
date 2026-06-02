# Sound Control

Self-use macOS menu bar app for controlling individual app volume without changing the global system volume.

## MVP Scope

- Process-level app volume and mute.
- Menu bar UI with one row per currently audible app.
- Per-app settings persisted by bundle identifier.
- CoreAudio Process Tap based audio path.
- No volume boost, browser-tab splitting, global hotkeys, installer, or notarization yet.

## Build

```bash
swift run SoundControlChecks
swift run SoundControlChecks --list-processes
swift build
Scripts/build-app.sh
```

The app bundle is written to `.build/app/SoundControl.app` and ad-hoc signed for local use.

`--list-processes` prints the apps that CoreAudio currently reports as producing output audio. If that list is empty while audio is playing, check macOS audio capture permission and restart the app.

For a local tap smoke test, play audio from a short-lived process and point the checker at its process name:

```bash
swift run SoundControlChecks --tap-name afplay
```

## Run

```bash
open .build/app/SoundControl.app
```

On first launch, macOS should prompt for Screen & System Audio Recording permission. Grant it, then restart the app if the process list or tap creation does not work immediately.
