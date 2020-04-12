import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

ColumnLayout {
    spacing: 0

    Rectangle {
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 30
        Layout.preferredHeight: 30
        Layout.fillWidth: true
        color: "#888888"

        Text {
            text: "PROCEDURES"
            color: "white"
            font.bold: true
            font.pointSize: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
        }
    }

    ListView {
        Layout.fillHeight: true
        Layout.fillWidth: true
        Layout.leftMargin: 10
        Layout.rightMargin: 10

        orientation: Qt.Vertical
        spacing: 10
        clip: true

        header: Rectangle {
            height: 10
            Layout.fillWidth: true
        }

        footer: Rectangle {
            height: 10
            Layout.fillWidth: true
        }
        
        model: simpleModel
        delegate: procedureStepDelegate

        highlight: Rectangle {
            color: "lightgreen"
        }
        highlightResizeDuration: 0
        focus: true
        keyNavigationEnabled: false
    }

    Rectangle {
        Layout.alignment: Qt.AlignBottom
        Layout.minimumHeight: 100
        Layout.preferredHeight: 100
        Layout.fillWidth: true
        color: "green"

        RowLayout {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/play_backwards.png"
                icon.color: "transparent"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/undo.png"
                icon.color: "transparent"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/play.png"
                icon.color: "transparent"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/stop.png"
                icon.color: "transparent"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/step_forward.png"
                icon.color: "transparent"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/advance.png"
                icon.color: "transparent"
            }
        }
    }

    ListModel {
        id: simpleModel
    
        ListElement {
            person: "PRIMARY"
            action: "Open Series Fill Valve"
        }

        ListElement {
            person: "PRIMARY"
            action: "Open Line Fill Valve"
        }

        ListElement {
            person: "SECONDARY"
            action: "Open Series Fill Valve Open Series Fill Valve Open Series Fill Valve"
        }
    }

    Component {
        id: procedureStepDelegate

        RowLayout {
            width: parent.width
            spacing: 10
            
            Text {
                text: index + 1 + "."
                font.bold: true
                font.pointSize: 10
                Layout.alignment: Qt.AlignTop
            }
            
            Text {
                text: person + ":"
                font.bold: true
                font.pointSize: 10
                color: "blue"
                Layout.alignment: Qt.AlignTop
            }
            
            Text {
                text: action
                font.pointSize: 10
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
            }
        }
    }
}
