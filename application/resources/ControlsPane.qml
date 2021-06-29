import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

import VisualizationArea 1.0 

ColumnLayout {

    property string buttonRed: "#FF0000"
    property string buttonGreen: "#00FF00"

    Rectangle {
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 30
        Layout.preferredHeight: 30
        Layout.fillWidth: true

        Text {
            text: "Control Panel"
            font.pointSize: 30
            font.weight: Font.Bold
        }
    }

    RowLayout {
        spacing: 50
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 100
        Layout.preferredHeight: 150

        Rectangle {
            Layout.preferredHeight: 100
            Layout.preferredWidth: 10
        }

        Repeater {
            model: controlsBridge.numOfComponents
            Rectangle {
                Layout.preferredHeight: 100
                Layout.preferredWidth: 70

                RoundButton {
                    id: button1
                    width: 70
                    height: 70
                    palette {
                        button: controlsBridge.isOpen[index] ? buttonGreen : buttonRed
                    }
                    onClicked: controlsBridge.isOpen[index] ? controlsBridge.toggle_off(index) : controlsBridge.toggle_on(index)
                }

                Text {
                    padding: 10
                    id: text1
                    anchors.top: button1.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    font.pointSize: 12
                    text: controlsBridge.components[index]
                }
            }
        }
    }
}
