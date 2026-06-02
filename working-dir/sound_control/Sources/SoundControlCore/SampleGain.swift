import Foundation

public enum SampleGain {
    public static func mappedSamples(
        input: [Float],
        inputChannels: Int,
        outputChannels: Int,
        gain: Float
    ) -> [Float] {
        guard inputChannels > 0, outputChannels > 0 else { return [] }
        let frameCount = input.count / inputChannels
        var output = [Float](repeating: 0, count: frameCount * outputChannels)
        output.withUnsafeMutableBufferPointer { outPtr in
            input.withUnsafeBufferPointer { inPtr in
                guard let inBase = inPtr.baseAddress, let outBase = outPtr.baseAddress else { return }
                apply(
                    inputSamples: inBase,
                    inputChannels: inputChannels,
                    frameCount: frameCount,
                    outputSamples: outBase,
                    outputChannels: outputChannels,
                    gain: gain
                )
            }
        }
        return output
    }

    @inline(__always)
    public static func apply(
        inputSamples: UnsafePointer<Float>,
        inputChannels: Int,
        frameCount: Int,
        outputSamples: UnsafeMutablePointer<Float>,
        outputChannels: Int,
        gain: Float
    ) {
        guard inputChannels > 0, outputChannels > 0, frameCount > 0 else { return }

        if inputChannels == outputChannels {
            let sampleCount = frameCount * inputChannels
            for index in 0..<sampleCount {
                outputSamples[index] = inputSamples[index] * gain
            }
            return
        }

        if inputChannels == 2 && outputChannels > 2 {
            for frame in 0..<frameCount {
                let inBase = frame * 2
                let outBase = frame * outputChannels
                for channel in 0..<outputChannels {
                    outputSamples[outBase + channel] = 0
                }
                outputSamples[outBase] = inputSamples[inBase] * gain
                outputSamples[outBase + 1] = inputSamples[inBase + 1] * gain
            }
            return
        }

        if inputChannels == 1 && outputChannels > 1 {
            for frame in 0..<frameCount {
                let sample = inputSamples[frame] * gain
                let outBase = frame * outputChannels
                for channel in 0..<outputChannels {
                    outputSamples[outBase + channel] = 0
                }
                outputSamples[outBase] = sample
                outputSamples[outBase + 1] = sample
            }
            return
        }

        for frame in 0..<frameCount {
            let inBase = frame * inputChannels
            let outBase = frame * outputChannels
            let copiedChannels = min(inputChannels, outputChannels)
            for channel in 0..<copiedChannels {
                outputSamples[outBase + channel] = inputSamples[inBase + channel] * gain
            }
            if copiedChannels < outputChannels {
                for channel in copiedChannels..<outputChannels {
                    outputSamples[outBase + channel] = 0
                }
            }
        }
    }
}
