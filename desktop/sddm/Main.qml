// SPDX-License-Identifier: MIT
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#0b110e"
    property bool authenticating: false
    function login() {
        if (authenticating || !username.text || !password.text) return
        authenticating = true
        status.text = "Signing in…"
        sddm.login(username.text, password.text, session.currentIndex)
    }
    Connections {
        target: sddm
        function onLoginFailed() {
            root.authenticating = false
            status.text = "Sign-in failed. Check your username and password."
            password.text = ""
            password.forceActiveFocus()
        }
    }
    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(740, parent.width - 64)
        spacing: 18
        Image {
            source: "logo.svg"
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            fillMode: Image.PreserveAspectFit
        }
        Label { text: "OPEN SECURITY WORKSTATION"; color: "#a7f39b"; Layout.alignment: Qt.AlignHCenter }
        Label { text: "Username"; color: "#a7f39b" }
        TextField {
            id: username
            objectName: "username"
            Layout.fillWidth: true
            placeholderText: "Username"
            focus: true
            enabled: !root.authenticating
            KeyNavigation.tab: password
            onAccepted: password.forceActiveFocus()
        }
        Label { text: "Password"; color: "#a7f39b" }
        TextField {
            id: password
            objectName: "password"
            Layout.fillWidth: true
            placeholderText: "Password"
            echoMode: TextInput.Password
            enabled: !root.authenticating
            onAccepted: root.login()
        }
        ComboBox {
            id: session
            Layout.fillWidth: true
            model: sessionModel
            textRole: "name"
            onCountChanged: { var index = find("STRATAGEM DARK"); if (index >= 0) currentIndex = index }
        }
        Button { text: "Sign in"; Layout.fillWidth: true; enabled: !root.authenticating; onClicked: root.login() }
        Label { id: status; text: config.boolValue("LiveSession") ? "Live test login: stratagem / stratagem" : "Sign in to your workstation"; color: "#a7f39b"; wrapMode: Text.Wrap; Layout.fillWidth: true }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Button { text: "Restart"; enabled: sddm.canReboot; onClicked: sddm.reboot() }
            Button { text: "Shut down"; enabled: sddm.canPowerOff; onClicked: sddm.powerOff() }
        }
    }
}
