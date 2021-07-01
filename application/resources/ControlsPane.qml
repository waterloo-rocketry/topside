import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

import VisualizationArea 1.0 

Column {
    property string buttonRed: "#FF0000"
    property string buttonGreen: "#00FF00"

    Rectangle {
        width: 150
        height: 40

        Text {
            text: "Control Panel"
            font.pointSize: 30
            font.weight: Font.Bold
        }
    }

    ScrollView {
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff
        width: 1200
        height: 130
    
        Row {
            padding: 20
            spacing: 100

            Repeater {
                model: controlsBridge.numOfComponents
                Rectangle {
                    height: 100
                    width: 70

                    RoundButton {
                        id: button1
                        width: 70
                        height: 70
                        palette {
                            button: controlsBridge.states[index] == "open" ? buttonGreen : buttonRed
                        }
                        onClicked: controlsBridge.states[index] == "open" ? controlsBridge.toggle_off(index) : controlsBridge.toggle_on(index)
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
}
