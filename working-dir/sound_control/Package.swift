// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "SoundControl",
    platforms: [
        .macOS("15.0")
    ],
    products: [
        .library(name: "SoundControlCore", targets: ["SoundControlCore"]),
        .executable(name: "SoundControl", targets: ["SoundControlApp"]),
        .executable(name: "SoundControlChecks", targets: ["SoundControlChecks"])
    ],
    targets: [
        .target(
            name: "SoundControlCore",
            path: "Sources/SoundControlCore",
            linkerSettings: [
                .linkedFramework("AppKit"),
                .linkedFramework("AudioToolbox"),
                .linkedFramework("CoreAudio")
            ]
        ),
        .executableTarget(
            name: "SoundControlApp",
            dependencies: ["SoundControlCore"],
            path: "Sources/SoundControlApp",
            linkerSettings: [
                .linkedFramework("AppKit")
            ]
        ),
        .executableTarget(
            name: "SoundControlChecks",
            dependencies: ["SoundControlCore"],
            path: "Checks/SoundControlChecks"
        )
    ]
)
