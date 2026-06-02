import Foundation
import SoundControlCore

enum CheckError: Error, LocalizedError {
    case failed(String)

    var errorDescription: String? {
        switch self {
        case let .failed(message):
            return message
        }
    }
}

func expect(_ condition: @autoclosure () -> Bool, _ message: String) throws {
    guard condition() else {
        throw CheckError.failed(message)
    }
}

func expectEqual(_ lhs: [Float], _ rhs: [Float], accuracy: Float, _ message: String) throws {
    guard lhs.count == rhs.count else {
        throw CheckError.failed("\(message): count \(lhs.count) != \(rhs.count)")
    }
    for index in lhs.indices {
        if abs(lhs[index] - rhs[index]) > accuracy {
            throw CheckError.failed("\(message): index \(index) \(lhs[index]) != \(rhs[index])")
        }
    }
}

func checkVolumeStore() throws {
    let url = FileManager.default.temporaryDirectory
        .appendingPathComponent(UUID().uuidString)
        .appendingPathComponent("volumes.json")
    let store = VolumeStore(fileURL: url)

    store.setVolume(1.5, for: "com.example.App")
    store.setMuted(true, for: "com.example.App")

    let reloaded = VolumeStore(fileURL: url)
    try expect(reloaded.setting(for: "com.example.App").volume == 1.0, "volume should clamp to 1.0")
    try expect(reloaded.setting(for: "com.example.App").muted, "mute should persist")
    try expect(!AppVolumeSetting().needsControl, "default setting should not need tap control")
    try expect(AppVolumeSetting(volume: 0.5).needsControl, "low volume should need tap control")
    try expect(AppVolumeSetting(volume: 1.0, muted: true).needsControl, "mute should need tap control")
}

func checkSampleGain() throws {
    try expectEqual(
        SampleGain.mappedSamples(input: [0.2, -0.4, 0.6, -0.8], inputChannels: 2, outputChannels: 2, gain: 0.5),
        [0.1, -0.2, 0.3, -0.4],
        accuracy: 0.0001,
        "same-channel gain"
    )

    try expectEqual(
        SampleGain.mappedSamples(input: [1.0, -1.0], inputChannels: 2, outputChannels: 4, gain: 0.25),
        [0.25, -0.25, 0.0, 0.0],
        accuracy: 0.0001,
        "stereo-to-multichannel gain"
    )

    try expectEqual(
        SampleGain.mappedSamples(input: [0.8, -0.2], inputChannels: 1, outputChannels: 2, gain: 0.5),
        [0.4, 0.4, -0.1, -0.1],
        accuracy: 0.0001,
        "mono-to-stereo gain"
    )
}

func checkAggregateInputMapping() throws {
    try expect(
        ProcessTapController.inputIndexForOutput(outputIndex: 0, inputBufferCount: 4, outputBufferCount: 2) == 2,
        "aggregate mapping should read the first tap buffer when aggregate input has extra device buffers"
    )
    try expect(
        ProcessTapController.inputIndexForOutput(outputIndex: 1, inputBufferCount: 4, outputBufferCount: 2) == 3,
        "aggregate mapping should read the second tap buffer when aggregate input has extra device buffers"
    )
    try expect(
        ProcessTapController.inputIndexForOutput(outputIndex: 0, inputBufferCount: 1, outputBufferCount: 2) == 0,
        "single input buffer should be reused for first output buffer"
    )
}

func checkTap(named nameFragment: String) throws {
    let deadline = Date().addingTimeInterval(5)
    let monitor = AudioProcessMonitor()
    var match: AudioApp?

    while Date() < deadline {
        let apps = monitor.refresh()
        match = apps.first { app in
            app.name.localizedCaseInsensitiveContains(nameFragment)
        }
        if match != nil {
            break
        }
        Thread.sleep(forTimeInterval: 0.2)
    }

    guard let app = match else {
        throw CheckError.failed("no active audio process matched '\(nameFragment)'")
    }

    let tap = ProcessTapController(app: app)
    tap.volume = 0.5
    try tap.activate()
    Thread.sleep(forTimeInterval: 1.0)
    try expect(tap.hasRenderedAudio, "tap should receive at least one IO callback")
    let peak = tap.lastInputPeak
    try expect(peak > 0.0, "tap input peak should be non-zero while source audio is playing")
    tap.invalidate()
    print("SoundControlChecks: tap PASS for \(app.name) pid=\(app.id) peak=\(peak)")
}

do {
    if CommandLine.arguments.contains("--list-processes") {
        let apps = AudioProcessMonitor().refresh()
        print("SoundControlChecks: active audio apps = \(apps.count)")
        for app in apps {
            print("\(app.id)\t\(app.name)\t\(app.bundleID ?? "-")\tobjects=\(app.processObjectIDs.count)")
        }
        exit(0)
    }

    if let tapIndex = CommandLine.arguments.firstIndex(of: "--tap-name") {
        let valueIndex = CommandLine.arguments.index(after: tapIndex)
        guard valueIndex < CommandLine.arguments.endIndex else {
            throw CheckError.failed("--tap-name requires a process name fragment")
        }
        try checkTap(named: CommandLine.arguments[valueIndex])
        exit(0)
    }

    try checkVolumeStore()
    try checkSampleGain()
    try checkAggregateInputMapping()
    print("SoundControlChecks: PASS")
} catch {
    fputs("SoundControlChecks: FAIL - \(error.localizedDescription)\n", stderr)
    exit(1)
}
