import AudioToolbox
import Foundation

public final class ProcessTapController {
    public let app: AudioApp

    public var volume: Float {
        get { targetVolume }
        set { targetVolume = Self.clamp(newValue) }
    }

    public var isMuted: Bool = false

    private var targetVolume: Float = 1.0
    private var currentVolume: Float = 1.0
    private var rampCoefficient: Float = 0.0007

    private let queue: DispatchQueue
    private var tapID: AudioObjectID = .unknown
    private var aggregateDeviceID: AudioObjectID = .unknown
    private var deviceProcID: AudioDeviceIOProcID?
    private var tapDescription: CATapDescription?
    private var activated = false
    private var renderCount: UInt64 = 0
    private var inputPeak: Float = 0.0

    public var hasRenderedAudio: Bool {
        renderCount > 0
    }

    public var lastInputPeak: Float {
        inputPeak
    }

    public init(app: AudioApp) {
        self.app = app
        self.queue = DispatchQueue(label: "SoundControl.ProcessTap.\(app.id)", qos: .userInitiated)
    }

    deinit {
        invalidate()
    }

    public func activate() throws {
        guard !activated else { return }

        let description = CATapDescription(stereoMixdownOfProcesses: app.processObjectIDs)
        description.uuid = UUID()
        description.muteBehavior = .mutedWhenTapped
        description.isPrivate = true

        var newTapID = AudioObjectID.unknown
        var err = AudioHardwareCreateProcessTap(description, &newTapID)
        guard err == noErr else {
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(err), userInfo: [
                NSLocalizedDescriptionKey: "AudioHardwareCreateProcessTap failed: \(err)"
            ])
        }

        tapDescription = description
        tapID = newTapID

        let outputDevice = try AudioDeviceID.readDefaultOutputDevice()
        let outputUID = try outputDevice.readDeviceUID()
        let aggregateUID = UUID().uuidString

        let aggregateDescription: [String: Any] = [
            kAudioAggregateDeviceNameKey: "SoundControl-\(app.id)",
            kAudioAggregateDeviceUIDKey: aggregateUID,
            kAudioAggregateDeviceMainSubDeviceKey: outputUID,
            kAudioAggregateDeviceIsPrivateKey: true,
            kAudioAggregateDeviceIsStackedKey: false,
            kAudioAggregateDeviceTapAutoStartKey: true,
            kAudioAggregateDeviceSubDeviceListKey: [
                [
                    kAudioSubDeviceUIDKey: outputUID
                ]
            ],
            kAudioAggregateDeviceTapListKey: [
                [
                    kAudioSubTapUIDKey: description.uuid.uuidString,
                    kAudioSubTapDriftCompensationKey: true
                ]
            ]
        ]

        var newAggregateID = AudioObjectID.unknown
        err = AudioHardwareCreateAggregateDevice(aggregateDescription as CFDictionary, &newAggregateID)
        guard err == noErr else {
            invalidate()
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(err), userInfo: [
                NSLocalizedDescriptionKey: "AudioHardwareCreateAggregateDevice failed: \(err)"
            ])
        }

        aggregateDeviceID = newAggregateID
        guard aggregateDeviceID.waitUntilReady(timeout: 2.0) else {
            invalidate()
            throw NSError(domain: "SoundControl.ProcessTapController", code: -1, userInfo: [
                NSLocalizedDescriptionKey: "Aggregate device did not become ready"
            ])
        }

        let sampleRate = (try? aggregateDeviceID.readNominalSampleRate()) ?? 48_000
        rampCoefficient = 1 - exp(-1 / (Float(sampleRate) * 0.030))

        err = AudioDeviceCreateIOProcIDWithBlock(&deviceProcID, aggregateDeviceID, queue) { [weak self] _, inputData, _, outputData, _ in
            guard let self else {
                Self.zero(outputData)
                return
            }
            self.process(inputData: inputData, outputData: outputData)
        }
        guard err == noErr else {
            invalidate()
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(err), userInfo: [
                NSLocalizedDescriptionKey: "AudioDeviceCreateIOProcIDWithBlock failed: \(err)"
            ])
        }

        err = AudioDeviceStart(aggregateDeviceID, deviceProcID)
        guard err == noErr else {
            invalidate()
            throw NSError(domain: NSOSStatusErrorDomain, code: Int(err), userInfo: [
                NSLocalizedDescriptionKey: "AudioDeviceStart failed: \(err)"
            ])
        }

        currentVolume = targetVolume
        activated = true
    }

    public static func inputIndexForOutput(
        outputIndex: Int,
        inputBufferCount: Int,
        outputBufferCount: Int
    ) -> Int {
        guard inputBufferCount > 0 else { return -1 }
        if inputBufferCount > outputBufferCount {
            return min(inputBufferCount - outputBufferCount + outputIndex, inputBufferCount - 1)
        }
        return min(outputIndex, inputBufferCount - 1)
    }

    public func invalidate() {
        if aggregateDeviceID.isValid {
            if let deviceProcID {
                let stopStatus = AudioDeviceStop(aggregateDeviceID, deviceProcID)
                if stopStatus != noErr {
                    NSLog("SoundControl AudioDeviceStop failed for \(app.name): \(stopStatus)")
                }

                let destroyProcStatus = AudioDeviceDestroyIOProcID(aggregateDeviceID, deviceProcID)
                if destroyProcStatus != noErr {
                    NSLog("SoundControl AudioDeviceDestroyIOProcID failed for \(app.name): \(destroyProcStatus)")
                }
                self.deviceProcID = nil
            }

            let aggregateStatus = AudioHardwareDestroyAggregateDevice(aggregateDeviceID)
            if aggregateStatus != noErr {
                NSLog("SoundControl AudioHardwareDestroyAggregateDevice failed for \(app.name): \(aggregateStatus)")
            }
            aggregateDeviceID = .unknown
        }

        if tapID.isValid {
            let tapStatus = AudioHardwareDestroyProcessTap(tapID)
            if tapStatus != noErr {
                NSLog("SoundControl AudioHardwareDestroyProcessTap failed for \(app.name): \(tapStatus)")
            }
            tapID = .unknown
        }

        tapDescription = nil
        activated = false
        renderCount = 0
        inputPeak = 0.0
    }

    private func process(
        inputData: UnsafePointer<AudioBufferList>,
        outputData: UnsafeMutablePointer<AudioBufferList>
    ) {
        if isMuted {
            Self.zero(outputData)
            return
        }

        let inputBuffers = UnsafeMutableAudioBufferListPointer(UnsafeMutablePointer(mutating: inputData))
        let outputBuffers = UnsafeMutableAudioBufferListPointer(outputData)
        renderCount &+= 1
        var callbackPeak: Float = 0.0

        for outputIndex in 0..<outputBuffers.count {
            let outputBuffer = outputBuffers[outputIndex]
            guard let outputPointer = outputBuffer.mData else { continue }

            let inputIndex = Self.inputIndexForOutput(
                outputIndex: outputIndex,
                inputBufferCount: inputBuffers.count,
                outputBufferCount: outputBuffers.count
            )
            guard inputIndex >= 0, inputIndex < inputBuffers.count else {
                memset(outputPointer, 0, Int(outputBuffer.mDataByteSize))
                continue
            }

            let inputBuffer = inputBuffers[inputIndex]
            guard let inputPointer = inputBuffer.mData else {
                memset(outputPointer, 0, Int(outputBuffer.mDataByteSize))
                continue
            }

            let inputChannels = max(1, Int(inputBuffer.mNumberChannels))
            let outputChannels = max(1, Int(outputBuffer.mNumberChannels))
            let inputSampleCount = Int(inputBuffer.mDataByteSize) / MemoryLayout<Float>.stride
            let outputSampleCount = Int(outputBuffer.mDataByteSize) / MemoryLayout<Float>.stride
            let frameCount = min(inputSampleCount / inputChannels, outputSampleCount / outputChannels)

            guard frameCount > 0 else {
                memset(outputPointer, 0, Int(outputBuffer.mDataByteSize))
                continue
            }

            let inputSamples = inputPointer.assumingMemoryBound(to: Float.self)
            let selectedInputSampleCount = frameCount * inputChannels
            for sampleIndex in 0..<selectedInputSampleCount {
                let absSample = abs(inputSamples[sampleIndex])
                if absSample > callbackPeak {
                    callbackPeak = absSample
                }
            }

            currentVolume += (targetVolume - currentVolume) * rampCoefficient
            SampleGain.apply(
                inputSamples: inputSamples,
                inputChannels: inputChannels,
                frameCount: frameCount,
                outputSamples: outputPointer.assumingMemoryBound(to: Float.self),
                outputChannels: outputChannels,
                gain: currentVolume
            )

            let writtenBytes = frameCount * outputChannels * MemoryLayout<Float>.stride
            if writtenBytes < Int(outputBuffer.mDataByteSize) {
                memset(outputPointer.advanced(by: writtenBytes), 0, Int(outputBuffer.mDataByteSize) - writtenBytes)
            }
        }

        inputPeak = callbackPeak
    }

    private static func zero(_ outputData: UnsafeMutablePointer<AudioBufferList>) {
        let outputBuffers = UnsafeMutableAudioBufferListPointer(outputData)
        for buffer in outputBuffers {
            if let data = buffer.mData {
                memset(data, 0, Int(buffer.mDataByteSize))
            }
        }
    }

    private static func clamp(_ value: Float) -> Float {
        guard value.isFinite else { return 1.0 }
        return max(0.0, min(1.0, value))
    }
}
