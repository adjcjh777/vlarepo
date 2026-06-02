import AppKit

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var menuController: MenuController?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        menuController = MenuController()
    }

    func applicationWillTerminate(_ notification: Notification) {
        menuController?.invalidate()
    }
}
