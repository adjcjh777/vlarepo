# Sound Control MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-use macOS menu bar app that controls per-process app volume without changing the global system volume.

**Architecture:** Use CoreAudio process taps. The menu app discovers active audio processes, persists per-app volume state, and creates a private aggregate device plus IOProc only when an app needs non-default volume or mute. The IOProc performs realtime-safe gain scaling and tears down CoreAudio resources in a fixed order.

**Tech Stack:** SwiftPM, Swift/AppKit, CoreAudio/AudioToolbox, XCTest, manual `.app` bundle script, ad-hoc codesign.

---

## File Structure

- `Package.swift`: SwiftPM package with `SoundControlCore` library, `SoundControl` executable, and tests.
- `Sources/SoundControlCore/CoreAudioObjects.swift`: CoreAudio object constants and property helpers.
- `Sources/SoundControlCore/AudioApp.swift`: process/app model and persistence identifier.
- `Sources/SoundControlCore/AudioProcessMonitor.swift`: CoreAudio HAL process list to app rows.
- `Sources/SoundControlCore/VolumeStore.swift`: JSON-backed per-app volume/mute storage.
- `Sources/SoundControlCore/SampleGain.swift`: pure gain/channel mapping helper used for tests and mirrored by realtime callback.
- `Sources/SoundControlCore/ProcessTapController.swift`: process tap, private aggregate device, IOProc, teardown.
- `Sources/SoundControlCore/AudioMixer.swift`: syncs `VolumeStore` state to active tap controllers.
- `Sources/SoundControlApp/AppDelegate.swift`: AppKit status item lifecycle.
- `Sources/SoundControlApp/MenuController.swift`: menu rows, sliders, mute buttons, refresh timer.
- `Sources/SoundControlApp/main.swift`: app entrypoint.
- `Resources/Info.plist`: menu-bar app flags and audio capture permission string.
- `Scripts/build-app.sh`: release build, app bundle assembly, ad-hoc signing.
- `Checks/SoundControlChecks/main.swift`: focused executable checks for persistence and gain mapping because this machine's Command Line Tools do not include XCTest.
- `README.md`: self-use run/build notes and current MVP limitations.

## Tasks

### Task 1: SwiftPM Skeleton

**Files:**
- Create: `Package.swift`
- Create: `Resources/Info.plist`
- Create: `Sources/SoundControlApp/main.swift`
- Create: `README.md`

- [ ] Create package manifest with one library target, one executable target, and one test target.
- [ ] Add `Info.plist` with `LSUIElement` and `NSAudioCaptureUsageDescription`.
- [ ] Add a minimal AppKit entrypoint that starts `NSApplication`.
- [ ] Run `swift build` and fix compiler errors before proceeding.

### Task 2: Core Models And Tests

**Files:**
- Create: `Sources/SoundControlCore/AudioApp.swift`
- Create: `Sources/SoundControlCore/VolumeStore.swift`
- Create: `Sources/SoundControlCore/SampleGain.swift`
- Create: `Checks/SoundControlChecks/main.swift`

- [ ] Implement `AudioApp` with PID, process object IDs, name, icon, bundle ID, helper-backed flag, and stable persistence identifier.
- [ ] Implement JSON storage for `volume` and `muted`, clamped to `0.0...1.0`.
- [ ] Implement pure sample gain/channel mapping for same-channel, stereo-to-multichannel, and mono-to-stereo cases.
- [ ] Run `swift run SoundControlChecks`.

### Task 3: Audio Process Discovery

**Files:**
- Create: `Sources/SoundControlCore/CoreAudioObjects.swift`
- Create: `Sources/SoundControlCore/AudioProcessMonitor.swift`

- [ ] Add CoreAudio property helpers for arrays, strings, bools, process PID, bundle ID, output-running status, default output device, device UID, and nominal sample rate.
- [ ] Implement process refresh using `kAudioHardwarePropertyProcessObjectList`.
- [ ] Map HAL process objects to `NSRunningApplication`, merge helper/XPC processes into parent apps via responsibility API or parent-process walk.
- [ ] Filter this app and obvious system audio daemons.
- [ ] Run `swift run SoundControlChecks` and `swift build`.

### Task 4: Menu UI And Mixer State

**Files:**
- Create: `Sources/SoundControlCore/AudioMixer.swift`
- Create: `Sources/SoundControlApp/AppDelegate.swift`
- Create: `Sources/SoundControlApp/MenuController.swift`
- Modify: `Sources/SoundControlApp/main.swift`

- [ ] Build an `NSStatusItem` menu with refresh, app rows, sliders, mute buttons, and quit item.
- [ ] Refresh process list on menu open and on a short timer.
- [ ] Update `VolumeStore` when sliders or mute buttons change.
- [ ] Sync store state to `AudioMixer`.
- [ ] Run `swift build`.

### Task 5: Process Tap Audio Path

**Files:**
- Create: `Sources/SoundControlCore/ProcessTapController.swift`
- Modify: `Sources/SoundControlCore/AudioMixer.swift`

- [ ] Create a `CATapDescription(stereoMixdownOfProcesses:)` for each controlled app.
- [ ] Use `.mutedWhenTapped` so the original app output is muted only while our aggregate IOProc is reading.
- [ ] Create a private aggregate device that contains the real default output device and the process tap.
- [ ] In the IOProc, copy input to output while applying ramped `volume` or zeroing when muted.
- [ ] Destroy resources in this order: stop device, destroy IOProc, destroy aggregate device, destroy process tap.
- [ ] Run `swift build`.

### Task 6: Bundle, Smoke Test, Commit

**Files:**
- Create: `Scripts/build-app.sh`
- Modify: `README.md`

- [ ] Build release binary and assemble `SoundControl.app`.
- [ ] Ad-hoc sign the app with `codesign --force --deep --sign -`.
- [ ] Run checks with `swift run SoundControlChecks`.
- [ ] Run build script.
- [ ] Inspect app bundle contents and signature.
- [ ] Stage only `working-dir/sound_control` files, commit with a concise message, and attempt push.

## MVP Acceptance

- `swift run SoundControlChecks` passes.
- `swift build` passes.
- `Scripts/build-app.sh` produces `SoundControl.app`.
- The app can be launched from the built bundle.
- Menu shows active audio processes.
- Changing a slider below 100% creates a tap for that process and changes only that process's output path.
- Returning an app to 100% and unmuted tears its tap down.
- Per-app settings survive app restart.

## Known MVP Limits

- Process-level only; no browser-tab or window-level control.
- No boost above 100%.
- No global hotkeys.
- No crossfade on output-device changes.
- No installer, notarization, or App Store support.
