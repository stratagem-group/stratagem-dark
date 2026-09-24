import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "stratagem.system-update"

  property bool updateAvailable: false

  function refresh() {
    if (!updateProc.running) updateProc.running = true
  }

  function clear() { updateAvailable = false }

  function runUpdate() {
    if (root.bar) root.bar.run("stratagem-launch-floating-terminal-with-presentation stratagem-update")
  }

  visible: updateAvailable
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  IpcHandler {
    target: "stratagem.system-update"

    function refresh(): void {
      root.broadcast("refresh")
    }

    function clear(): void {
      root.broadcast("clear")
    }
  }

  Process {
    id: updateProc
    command: ["stratagem-update-available"]
    onExited: function(exitCode) {
      root.updateAvailable = exitCode === 0
    }
  }

  Timer {
    interval: 21600000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "\uf021"
    slotSize: Style.bar.statusSlot
    fontSize: Style.font.caption
    tooltipText: "Pending STRATAGEM DARK Updates"
    onPressed: root.runUpdate()
  }
}
