import AudioToolbox
import Foundation

public enum CoreAudioReadError: Error, LocalizedError {
    case propertyDataSize(AudioObjectPropertyAddress, OSStatus)
    case propertyData(AudioObjectPropertyAddress, OSStatus)
    case invalidProcess(pid_t)
    case systemOnly

    public var errorDescription: String? {
        switch self {
        case let .propertyDataSize(address, status):
            return "Failed to read CoreAudio property size for \(address): \(status)"
        case let .propertyData(address, status):
            return "Failed to read CoreAudio property data for \(address): \(status)"
        case let .invalidProcess(pid):
            return "Invalid CoreAudio process identifier: \(pid)"
        case .systemOnly:
            return "This CoreAudio property can only be read from the system object."
        }
    }
}

public extension AudioObjectID {
    static let system = AudioObjectID(kAudioObjectSystemObject)
    static let unknown = AudioObjectID(kAudioObjectUnknown)

    var isValid: Bool {
        self != .unknown
    }

    static func readProcessList() throws -> [AudioObjectID] {
        try AudioObjectID.system.readArray(
            kAudioHardwarePropertyProcessObjectList,
            defaultValue: AudioObjectID.unknown
        )
    }

    static func readDeviceList() throws -> [AudioDeviceID] {
        try AudioObjectID.system.readArray(
            kAudioHardwarePropertyDevices,
            defaultValue: AudioDeviceID.unknown
        )
    }

    func readProcessPID() throws -> pid_t {
        try read(kAudioProcessPropertyPID, defaultValue: pid_t(0))
    }

    func readProcessBundleID() -> String? {
        guard let result = try? readString(kAudioProcessPropertyBundleID), !result.isEmpty else {
            return nil
        }
        return result
    }

    func readProcessIsRunning() -> Bool {
        (try? readBool(kAudioProcessPropertyIsRunning)) ?? false
    }

    func readProcessIsRunningOutput() -> Bool {
        (try? readBool(kAudioProcessPropertyIsRunningOutput)) ?? readProcessIsRunning()
    }

    func readAudioTapStreamBasicDescription() throws -> AudioStreamBasicDescription {
        try read(kAudioTapPropertyFormat, defaultValue: AudioStreamBasicDescription())
    }

    func waitUntilReady(timeout: TimeInterval) -> Bool {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if (try? (self as AudioDeviceID).readNominalSampleRate()) != nil {
                return true
            }
            usleep(20_000)
        }
        return false
    }
}

public extension AudioDeviceID {
    static func readDefaultOutputDevice() throws -> AudioDeviceID {
        try AudioObjectID.system.read(
            kAudioHardwarePropertyDefaultOutputDevice,
            defaultValue: AudioDeviceID.unknown
        )
    }

    func readDeviceUID() throws -> String {
        try readString(kAudioDevicePropertyDeviceUID)
    }

    func readDeviceName() throws -> String {
        try readString(kAudioObjectPropertyName)
    }

    func readNominalSampleRate() throws -> Float64 {
        try read(kAudioDevicePropertyNominalSampleRate, defaultValue: Float64(48_000))
    }
}

public extension AudioObjectID {
    func readArray<T>(
        _ selector: AudioObjectPropertySelector,
        scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal,
        element: AudioObjectPropertyElement = kAudioObjectPropertyElementMain,
        defaultValue: T
    ) throws -> [T] {
        try readArray(
            AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: element),
            defaultValue: defaultValue
        )
    }

    func readArray<T>(
        _ inAddress: AudioObjectPropertyAddress,
        defaultValue: T
    ) throws -> [T] {
        var address = inAddress
        var dataSize: UInt32 = 0
        var err = AudioObjectGetPropertyDataSize(self, &address, 0, nil, &dataSize)
        guard err == noErr else {
            throw CoreAudioReadError.propertyDataSize(inAddress, err)
        }

        let count = Int(dataSize) / MemoryLayout<T>.stride
        guard count > 0 else { return [] }
        var values = [T](repeating: defaultValue, count: count)
        err = values.withUnsafeMutableBufferPointer { buffer in
            AudioObjectGetPropertyData(self, &address, 0, nil, &dataSize, buffer.baseAddress!)
        }
        guard err == noErr else {
            throw CoreAudioReadError.propertyData(inAddress, err)
        }
        return values
    }

    func read<T, Q>(
        _ selector: AudioObjectPropertySelector,
        scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal,
        element: AudioObjectPropertyElement = kAudioObjectPropertyElementMain,
        defaultValue: T,
        qualifier: Q
    ) throws -> T {
        var qualifierValue = qualifier
        let qualifierSize = UInt32(MemoryLayout<Q>.size(ofValue: qualifier))
        return try withUnsafeMutablePointer(to: &qualifierValue) { pointer in
            try read(
                AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: element),
                defaultValue: defaultValue,
                qualifierSize: qualifierSize,
                qualifierData: pointer
            )
        }
    }

    func read<T>(
        _ selector: AudioObjectPropertySelector,
        scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal,
        element: AudioObjectPropertyElement = kAudioObjectPropertyElementMain,
        defaultValue: T
    ) throws -> T {
        try read(
            AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: element),
            defaultValue: defaultValue
        )
    }

    func readString(
        _ selector: AudioObjectPropertySelector,
        scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal,
        element: AudioObjectPropertyElement = kAudioObjectPropertyElementMain
    ) throws -> String {
        try read(
            AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: element),
            defaultValue: "" as CFString
        ) as String
    }

    func readBool(
        _ selector: AudioObjectPropertySelector,
        scope: AudioObjectPropertyScope = kAudioObjectPropertyScopeGlobal,
        element: AudioObjectPropertyElement = kAudioObjectPropertyElementMain
    ) throws -> Bool {
        let value: UInt32 = try read(
            AudioObjectPropertyAddress(mSelector: selector, mScope: scope, mElement: element),
            defaultValue: UInt32(0)
        )
        return value != 0
    }

    private func read<T>(
        _ inAddress: AudioObjectPropertyAddress,
        defaultValue: T,
        qualifierSize: UInt32 = 0,
        qualifierData: UnsafeRawPointer? = nil
    ) throws -> T {
        var address = inAddress
        var dataSize: UInt32 = 0
        var err = AudioObjectGetPropertyDataSize(self, &address, qualifierSize, qualifierData, &dataSize)
        guard err == noErr else {
            throw CoreAudioReadError.propertyDataSize(inAddress, err)
        }

        var value = defaultValue
        err = withUnsafeMutablePointer(to: &value) { pointer in
            AudioObjectGetPropertyData(self, &address, qualifierSize, qualifierData, &dataSize, pointer)
        }
        guard err == noErr else {
            throw CoreAudioReadError.propertyData(inAddress, err)
        }
        return value
    }
}

private extension UInt32 {
    var fourCharString: String {
        String(cString: [
            UInt8((self >> 24) & 0xFF),
            UInt8((self >> 16) & 0xFF),
            UInt8((self >> 8) & 0xFF),
            UInt8(self & 0xFF),
            0
        ])
    }
}

extension AudioObjectPropertyAddress: @retroactive CustomStringConvertible {
    public var description: String {
        "\(mSelector.fourCharString)/\(mScope.fourCharString)/\(mElement.fourCharString)"
    }
}
