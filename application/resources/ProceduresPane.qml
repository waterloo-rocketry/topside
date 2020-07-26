import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

ColumnLayout {
    spacing: 0

    // TODO(jacob): Investigate if this connection logic can/should be moved into Python
    Component.onCompleted: {
        proceduresBridge.gotoStep.connect(proceduresList.gotoStep)
    }

    Rectangle {
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 30
        Layout.preferredHeight: 30
        Layout.fillWidth: true
        color: "#888888"

        Text {
            text: "PROCEDURES"
            color: "white"
            font.pointSize: 10
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
        }
    }

    ListView {
        id: proceduresList
        Layout.fillHeight: true
        Layout.fillWidth: true
        Layout.leftMargin: 10
        Layout.rightMargin: 10

        orientation: Qt.Vertical
        spacing: 10
        clip: true

        ScrollBar.vertical: ScrollBar {
            width: 15
        }

        header: Rectangle {
            height: 10
            Layout.fillWidth: true
        }

        footer: Rectangle {
            height: 10
            Layout.fillWidth: true
        }
        
        highlight: Rectangle {
            color: "lightgreen"
        }

        highlightResizeDuration: 0
        highlightMoveDuration: 100
        highlightMoveVelocity: -1

        boundsBehavior: Flickable.DragOverBounds

        focus: true
        keyNavigationEnabled: false

        model: proceduresBridge.steps
        delegate: procedureStepDelegate

        function gotoStep(idx) {
            currentIndex = idx
        }
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

                onClicked: proceduresBridge.playBackwards()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/undo.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.undo()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.color: "transparent"
                property bool is_play: true
                icon.source: is_play ? "themes/default/play.png" : "themes/default/pause.png"
                
                onClicked: {
                    if (is_play) {
                        proceduresBridge.play()
                    } else {
                        proceduresBridge.pause()
                    }
                    is_play = !is_play
                }
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/stop.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.stop()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/step_forward.png"
                icon.color: "transparent"

                // TODO(jacob): We connect both clicked and doubleClicked to stepForward because
                // there seems to be some sort of debouncing/delay built in that prevents clicking
                // twice in quick succession from advancing steps twice. For now, we choose to
                // explicitly recognize a double click as identical to a click. Investigate if this
                // is really the best way to do things or if there's a better way to get rid of the
                // delay.
                onClicked: proceduresBridge.stepForward()
                onDoubleClicked: proceduresBridge.stepForward()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/advance.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.advance()
            }
        }
    }

    Component {
        id: procedureStepDelegate

        RowLayout {
            width: proceduresList.width
            spacing: 10
            
            Text {
                text: model.index + 1 + "."
                font.bold: true
                font.pointSize: 10
                Layout.alignment: Qt.AlignTop
            }
            
            Text {
                text: model.person + ":"
                font.bold: true
                font.pointSize: 10
                color: "blue"
                Layout.alignment: Qt.AlignTop
            }
            
            Text {
                text: model.step
                font.pointSize: 10
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
            }
        }
    }
}
