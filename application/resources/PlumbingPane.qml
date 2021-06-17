import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

import VisualizationArea 1.0 

ColumnLayout {
    spacing: 0

    property string plumbHeaderBg: "#888888"
    property string plumbHeaderTxt: "#ffffff"

    Component.onCompleted: {
        plumbingBridge.engineLoaded.connect(plumbingVisualizationArea.visualizer.uploadEngineInstance)
    }

    Rectangle {
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 30
        Layout.preferredHeight: 30
        Layout.fillWidth: true
        color: plumbHeaderBg

        Text {
            text: "PLUMBING"
            color: plumbHeaderTxt
            font.pointSize: 10
            font.weight: Font.Bold
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
        }
    }

    VisualizationArea {
        id: plumbingVisualizationArea

        width: parent.width
        height: parent.height
        Layout.fillHeight: true
        Layout.fillWidth: true
    }

    Rectangle {
        property string plumbFooterBg: "#843179"

        Layout.alignment: Qt.AlignBottom
        Layout.minimumHeight: 100
        Layout.preferredHeight: 100
        Layout.fillWidth: true
        color: plumbFooterBg

        RowLayout {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/play_backwards.png"
                icon.color: "transparent"

                onClicked: plumbingBridge.timePlayBackwards()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/step_backwards.png"
                icon.color: "transparent"

                onClicked: plumbingBridge.timeStepBackwards()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.color: "transparent"
                icon.source: plumbingBridge.paused ?
                    "themes/default/play.png" : "themes/default/pause.png"

                onClicked: {
                    if (plumbingBridge.paused) {
                        plumbingBridge.timePlay()
                    } else {
                        plumbingBridge.timePause()
                    }
                }
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/stop.png"
                icon.color: "transparent"

                onClicked: plumbingBridge.timeStop()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/step_forward.png"
                icon.color: "transparent"

                onClicked: {
                    plumbingBridge.timeStepForward();
                }
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/advance.png"
                icon.color: "transparent"

                onClicked: {
                    plumbingBridge.timeAdvance();
                }
            }
        }
    }
}
