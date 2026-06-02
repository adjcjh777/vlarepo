import Foundation

public final class AudioMixer {
    private let store: VolumeStore
    private var taps: [pid_t: ProcessTapController] = [:]
    public private(set) var lastErrors: [pid_t: String] = [:]

    public init(store: VolumeStore) {
        self.store = store
    }

    deinit {
        invalidateAll()
    }

    public func sync(apps: [AudioApp]) {
        let activePIDs = Set(apps.map(\.id))
        for pid in taps.keys where !activePIDs.contains(pid) {
            taps.removeValue(forKey: pid)?.invalidate()
            lastErrors.removeValue(forKey: pid)
        }

        for app in apps {
            let setting = store.setting(for: app.persistenceIdentifier)
            guard setting.needsControl else {
                taps.removeValue(forKey: app.id)?.invalidate()
                lastErrors.removeValue(forKey: app.id)
                continue
            }

            if let existing = taps[app.id], existing.app.processObjectIDs == app.processObjectIDs {
                existing.volume = setting.volume
                existing.isMuted = setting.muted
                lastErrors.removeValue(forKey: app.id)
                continue
            }

            taps.removeValue(forKey: app.id)?.invalidate()

            do {
                let tap = ProcessTapController(app: app)
                tap.volume = setting.volume
                tap.isMuted = setting.muted
                try tap.activate()
                taps[app.id] = tap
                lastErrors.removeValue(forKey: app.id)
            } catch {
                let message = error.localizedDescription
                lastErrors[app.id] = message
                NSLog("SoundControl failed to activate tap for \(app.name): \(message)")
            }
        }
    }

    public func error(for app: AudioApp) -> String? {
        lastErrors[app.id]
    }

    public func invalidateAll() {
        for tap in taps.values {
            tap.invalidate()
        }
        taps.removeAll()
        lastErrors.removeAll()
    }
}
