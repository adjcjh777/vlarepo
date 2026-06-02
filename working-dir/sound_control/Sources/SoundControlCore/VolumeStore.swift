import Foundation

public struct AppVolumeSetting: Codable, Equatable {
    public var volume: Float
    public var muted: Bool

    public init(volume: Float = 1.0, muted: Bool = false) {
        self.volume = Self.clamp(volume)
        self.muted = muted
    }

    public var needsControl: Bool {
        muted || volume < 0.999
    }

    private static func clamp(_ value: Float) -> Float {
        guard value.isFinite else { return 1.0 }
        return max(0.0, min(1.0, value))
    }

    public mutating func setVolume(_ newValue: Float) {
        volume = Self.clamp(newValue)
    }
}

public final class VolumeStore {
    public private(set) var settings: [String: AppVolumeSetting]
    private let fileURL: URL

    public init(fileURL: URL = VolumeStore.defaultFileURL()) {
        self.fileURL = fileURL
        self.settings = Self.load(from: fileURL)
    }

    public func setting(for identifier: String) -> AppVolumeSetting {
        settings[identifier] ?? AppVolumeSetting()
    }

    public func setVolume(_ volume: Float, for identifier: String) {
        var setting = settings[identifier] ?? AppVolumeSetting()
        setting.setVolume(volume)
        settings[identifier] = setting
        save()
    }

    public func setMuted(_ muted: Bool, for identifier: String) {
        var setting = settings[identifier] ?? AppVolumeSetting()
        setting.muted = muted
        settings[identifier] = setting
        save()
    }

    public func resetDefaultIfPossible(for identifier: String) {
        guard let setting = settings[identifier], !setting.needsControl else { return }
        settings.removeValue(forKey: identifier)
        save()
    }

    public func save() {
        do {
            try FileManager.default.createDirectory(
                at: fileURL.deletingLastPathComponent(),
                withIntermediateDirectories: true
            )
            let data = try JSONEncoder.sortedPrettyPrinted.encode(settings)
            try data.write(to: fileURL, options: .atomic)
        } catch {
            NSLog("SoundControl VolumeStore save failed: \(error.localizedDescription)")
        }
    }

    private static func load(from fileURL: URL) -> [String: AppVolumeSetting] {
        do {
            let data = try Data(contentsOf: fileURL)
            return try JSONDecoder().decode([String: AppVolumeSetting].self, from: data)
        } catch {
            return [:]
        }
    }

    public static func defaultFileURL() -> URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)
            .first ?? URL(fileURLWithPath: NSTemporaryDirectory())
        return base
            .appendingPathComponent("SoundControl", isDirectory: true)
            .appendingPathComponent("volumes.json")
    }
}

private extension JSONEncoder {
    static var sortedPrettyPrinted: JSONEncoder {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return encoder
    }
}
