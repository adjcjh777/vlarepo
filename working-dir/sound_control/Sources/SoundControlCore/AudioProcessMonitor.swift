import AppKit
import AudioToolbox
import Darwin

public final class AudioProcessMonitor {
    public private(set) var activeApps: [AudioApp] = []

    private static let systemDaemonPrefixes = [
        "com.apple.siri",
        "com.apple.Siri",
        "com.apple.audio",
        "com.apple.coreaudio",
        "com.apple.mediaremote",
        "com.apple.notificationcenter",
        "com.apple.NotificationCenter",
        "com.apple.UserNotifications",
        "com.apple.systemsound",
        "com.apple.corespeech",
        "com.apple.CoreSpeech",
        "com.apple.speech"
    ]

    private static let systemDaemonNames = [
        "coreaudiod",
        "audiomxd",
        "systemsoundserverd",
        "systemsoundserv",
        "corespeech",
        "speechrecognitiond"
    ]

    private typealias ResponsibilityFunc = @convention(c) (pid_t) -> pid_t

    public init() {}

    @discardableResult
    public func refresh() -> [AudioApp] {
        do {
            activeApps = try readActiveApps()
        } catch {
            NSLog("SoundControl process refresh failed: \(error.localizedDescription)")
            activeApps = []
        }
        return activeApps
    }

    private func readActiveApps() throws -> [AudioApp] {
        let processObjects = try AudioObjectID.readProcessList()
        let runningApps = NSWorkspace.shared.runningApplications
        let runningAppsByPID = Dictionary(
            runningApps.map { ($0.processIdentifier, $0) },
            uniquingKeysWith: { _, latest in latest }
        )
        let myPID = ProcessInfo.processInfo.processIdentifier
        var appsByPID: [pid_t: AudioApp] = [:]

        for objectID in processObjects {
            guard let pid = try? objectID.readProcessPID(), pid > 0, pid != myPID else { continue }
            guard objectID.readProcessIsRunningOutput() else { continue }

            let directApp = runningAppsByPID[pid]
            let isRealApp = directApp?.bundleURL?.pathExtension == "app"
            let resolvedApp = isRealApp ? directApp : findResponsibleApp(for: pid, in: runningAppsByPID)
            let parentPID = resolvedApp?.processIdentifier ?? pid
            let isHelper = parentPID != pid
            let bundleID = resolvedApp?.bundleIdentifier ?? objectID.readProcessBundleID()
            let name = resolvedApp?.localizedName
                ?? objectID.readProcessBundleID()?.components(separatedBy: ".").last
                ?? processName(for: pid)
                ?? "Unknown \(pid)"

            guard !isSystemDaemon(bundleID: bundleID, name: name) else { continue }

            let icon = resolvedApp?.icon
                ?? NSImage(systemSymbolName: "app.fill", accessibilityDescription: nil)
                ?? NSWorkspace.shared.icon(for: .applicationBundle)

            if let existing = appsByPID[parentPID] {
                var objectIDs = existing.processObjectIDs
                if !objectIDs.contains(objectID) {
                    objectIDs.append(objectID)
                    objectIDs.sort()
                }
                appsByPID[parentPID] = AudioApp(
                    id: existing.id,
                    processObjectIDs: objectIDs,
                    name: existing.name,
                    icon: existing.icon,
                    bundleID: existing.bundleID,
                    isHelperBacked: existing.isHelperBacked || isHelper
                )
            } else {
                appsByPID[parentPID] = AudioApp(
                    id: parentPID,
                    processObjectIDs: [objectID],
                    name: name,
                    icon: icon,
                    bundleID: bundleID,
                    isHelperBacked: isHelper
                )
            }
        }

        return appsByPID.values.sorted {
            $0.name.localizedCaseInsensitiveCompare($1.name) == .orderedAscending
        }
    }

    private func isSystemDaemon(bundleID: String?, name: String) -> Bool {
        if let bundleID, Self.systemDaemonPrefixes.contains(where: { bundleID.hasPrefix($0) }) {
            return true
        }

        let lowercasedName = name.lowercased()
        return Self.systemDaemonNames.contains { lowercasedName.hasPrefix($0) }
    }

    private func findResponsibleApp(
        for pid: pid_t,
        in runningAppsByPID: [pid_t: NSRunningApplication]
    ) -> NSRunningApplication? {
        if let responsiblePID = responsiblePID(for: pid),
           let app = runningAppsByPID[responsiblePID],
           app.bundleURL?.pathExtension == "app" {
            return app
        }

        var currentPID = pid
        var visited = Set<pid_t>()

        while currentPID > 1 && !visited.contains(currentPID) {
            visited.insert(currentPID)

            if let app = runningAppsByPID[currentPID],
               app.bundleURL?.pathExtension == "app" {
                return app
            }

            guard let parentPID = parentPID(for: currentPID), parentPID != currentPID else {
                break
            }
            currentPID = parentPID
        }

        return nil
    }

    private func responsiblePID(for pid: pid_t) -> pid_t? {
        guard let symbol = dlsym(UnsafeMutableRawPointer(bitPattern: -1), "responsibility_get_pid_responsible_for_pid") else {
            return nil
        }
        let function = unsafeBitCast(symbol, to: ResponsibilityFunc.self)
        let responsible = function(pid)
        return responsible > 0 && responsible != pid ? responsible : nil
    }

    private func parentPID(for pid: pid_t) -> pid_t? {
        var info = kinfo_proc()
        var size = MemoryLayout<kinfo_proc>.stride
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, pid]
        guard sysctl(&mib, u_int(mib.count), &info, &size, nil, 0) == 0 else {
            return nil
        }
        return info.kp_eproc.e_ppid
    }

    private func processName(for pid: pid_t) -> String? {
        var buffer = [CChar](repeating: 0, count: Int(MAXPATHLEN))
        let length = proc_name(pid, &buffer, UInt32(buffer.count))
        guard length > 0 else { return nil }
        return String(cString: buffer)
    }
}
