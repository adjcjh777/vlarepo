import AppKit
import SoundControlCore

final class MenuController: NSObject, NSMenuDelegate {
    private let statusItem: NSStatusItem
    private let menu = NSMenu()
    private let monitor = AudioProcessMonitor()
    private let store = VolumeStore()
    private lazy var mixer = AudioMixer(store: store)
    private var timer: Timer?
    private var rowControllers: [AppRowController] = []

    override init() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        super.init()

        statusItem.button?.image = NSImage(systemSymbolName: "speaker.wave.2.fill", accessibilityDescription: "Sound Control")
        statusItem.button?.toolTip = "Sound Control"
        menu.delegate = self
        statusItem.menu = menu

        refresh()
        timer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            self?.refresh()
        }
    }

    func invalidate() {
        timer?.invalidate()
        timer = nil
        mixer.invalidateAll()
    }

    func menuWillOpen(_ menu: NSMenu) {
        refresh()
    }

    @objc private func refreshAction() {
        refresh()
    }

    @objc private func quitAction() {
        NSApp.terminate(nil)
    }

    private func refresh() {
        let apps = monitor.refresh()
        mixer.sync(apps: apps)
        rebuildMenu(apps: apps)
    }

    private func rebuildMenu(apps: [AudioApp]) {
        rowControllers.removeAll()
        menu.removeAllItems()

        let titleItem = NSMenuItem(title: "Sound Control", action: nil, keyEquivalent: "")
        titleItem.isEnabled = false
        menu.addItem(titleItem)
        menu.addItem(.separator())

        if apps.isEmpty {
            let emptyItem = NSMenuItem(title: "没有检测到正在输出音频的应用", action: nil, keyEquivalent: "")
            emptyItem.isEnabled = false
            menu.addItem(emptyItem)
        } else {
            for app in apps {
                let row = AppRowController(app: app, store: store) { [weak self] in
                    guard let self else { return }
                    self.mixer.sync(apps: self.monitor.activeApps)
                }
                rowControllers.append(row)

                let item = NSMenuItem()
                item.view = row.view
                menu.addItem(item)
            }
        }

        menu.addItem(.separator())
        menu.addItem(NSMenuItem(title: "刷新", action: #selector(refreshAction), keyEquivalent: "r"))
        menu.items.last?.target = self
        menu.addItem(NSMenuItem(title: "退出", action: #selector(quitAction), keyEquivalent: "q"))
        menu.items.last?.target = self
    }
}

private final class AppRowController: NSObject {
    let view: NSView

    private let app: AudioApp
    private let store: VolumeStore
    private let onChange: () -> Void
    private let slider: NSSlider
    private let muteButton: NSButton
    private let percentLabel: NSTextField

    init(app: AudioApp, store: VolumeStore, onChange: @escaping () -> Void) {
        self.app = app
        self.store = store
        self.onChange = onChange

        let setting = store.setting(for: app.persistenceIdentifier)
        view = NSView(frame: NSRect(x: 0, y: 0, width: 360, height: 48))

        let iconView = NSImageView(frame: NSRect(x: 10, y: 10, width: 28, height: 28))
        iconView.image = app.icon
        iconView.imageScaling = .scaleProportionallyUpOrDown
        view.addSubview(iconView)

        let nameLabel = NSTextField(labelWithString: app.name)
        nameLabel.frame = NSRect(x: 48, y: 25, width: 168, height: 17)
        nameLabel.lineBreakMode = .byTruncatingTail
        nameLabel.font = .systemFont(ofSize: 13, weight: .medium)
        view.addSubview(nameLabel)

        let detail = app.isHelperBacked ? "进程级 · helper" : "进程级"
        let detailLabel = NSTextField(labelWithString: detail)
        detailLabel.frame = NSRect(x: 48, y: 7, width: 120, height: 15)
        detailLabel.textColor = .secondaryLabelColor
        detailLabel.font = .systemFont(ofSize: 11)
        view.addSubview(detailLabel)

        slider = NSSlider(value: Double(setting.volume), minValue: 0.0, maxValue: 1.0, target: nil, action: nil)
        slider.frame = NSRect(x: 165, y: 12, width: 115, height: 24)
        view.addSubview(slider)

        percentLabel = NSTextField(labelWithString: "\(Int(round(setting.volume * 100)))%")
        percentLabel.frame = NSRect(x: 284, y: 16, width: 38, height: 16)
        percentLabel.alignment = .right
        percentLabel.font = .monospacedDigitSystemFont(ofSize: 11, weight: .regular)
        percentLabel.textColor = .secondaryLabelColor
        view.addSubview(percentLabel)

        muteButton = NSButton(frame: NSRect(x: 326, y: 12, width: 28, height: 24))
        muteButton.title = ""
        muteButton.bezelStyle = .texturedRounded
        view.addSubview(muteButton)

        super.init()

        slider.target = self
        slider.action = #selector(sliderChanged(_:))
        muteButton.target = self
        muteButton.action = #selector(muteChanged(_:))
        updateMuteIcon(muted: setting.muted)
    }

    @objc private func sliderChanged(_ sender: NSSlider) {
        let volume = Float(sender.doubleValue)
        store.setVolume(volume, for: app.persistenceIdentifier)
        percentLabel.stringValue = "\(Int(round(volume * 100)))%"
        store.resetDefaultIfPossible(for: app.persistenceIdentifier)
        onChange()
    }

    @objc private func muteChanged(_ sender: NSButton) {
        let newMuted = !store.setting(for: app.persistenceIdentifier).muted
        store.setMuted(newMuted, for: app.persistenceIdentifier)
        updateMuteIcon(muted: newMuted)
        store.resetDefaultIfPossible(for: app.persistenceIdentifier)
        onChange()
    }

    private func updateMuteIcon(muted: Bool) {
        let symbolName = muted ? "speaker.slash.fill" : "speaker.wave.2.fill"
        muteButton.image = NSImage(systemSymbolName: symbolName, accessibilityDescription: muted ? "Unmute" : "Mute")
        muteButton.toolTip = muted ? "取消静音" : "静音"
    }
}
