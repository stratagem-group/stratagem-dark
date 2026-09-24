import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "stratagem.menu"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "> SD_"
    fontFamily: "monospace"
    horizontalMargin: 7.5
    onPressed: function(button) {
      if (!root.bar) return
      if (button === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("stratagem-shell shell toggle stratagem.menu '{\"menu\":\"root\"}'")
    }
  }
}
