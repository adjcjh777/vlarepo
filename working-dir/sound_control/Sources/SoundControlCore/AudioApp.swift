import AppKit
import AudioToolbox

public struct AudioApp: Identifiable, Hashable {
    public let id: pid_t
    public let processObjectIDs: [AudioObjectID]
    public let name: String
    public let icon: NSImage
    public let bundleID: String?
    public let isHelperBacked: Bool

    public init(
        id: pid_t,
        processObjectIDs: [AudioObjectID],
        name: String,
        icon: NSImage,
        bundleID: String?,
        isHelperBacked: Bool = false
    ) {
        self.id = id
        self.processObjectIDs = processObjectIDs
        self.name = name
        self.icon = icon
        self.bundleID = bundleID
        self.isHelperBacked = isHelperBacked
    }

    public var persistenceIdentifier: String {
        if let bundleID, !bundleID.isEmpty {
            return bundleID
        }
        return "name:\(name)"
    }

    public func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }

    public static func == (lhs: AudioApp, rhs: AudioApp) -> Bool {
        lhs.id == rhs.id
    }
}
