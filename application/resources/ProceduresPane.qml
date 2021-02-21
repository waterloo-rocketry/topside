import QtQuick 2.7

import QtQuick.Controls 2.14
import QtQuick.Layouts 1.0

ColumnLayout {
    spacing: 0

    property string procHeaderBg: "#888888"
    property string procHeaderTxt: "#ffffff"

    Component.onCompleted: {
        proceduresBridge.gotoStep.connect(proceduresList.gotoStep)
    }

    Rectangle {
        Layout.alignment: Qt.AlignTop
        Layout.minimumHeight: 30
        Layout.preferredHeight: 30
        Layout.fillWidth: true
        color: procHeaderBg

        Text {
            text: "PROCEDURES"
            color: procHeaderTxt
            font.pointSize: 10
            font.weight: Font.Bold
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
        }
    }

    ListView {
        id: proceduresList
        Layout.fillHeight: true
        Layout.fillWidth: true

        orientation: Qt.Vertical
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

        boundsBehavior: Flickable.DragOverBounds

        focus: true
        keyNavigationEnabled: false

        model: proceduresBridge.steps
        delegate: procedureStepDelegate

        function gotoStep(idx) {
            currentIndex = idx
        }
    }

    Component {
        id: procedureStepDelegate

        Rectangle {
            property bool inPostNode: proceduresBridge.stepPosition == 'After'

            property string stepHighlightBgPre: "#d8fff7"
            property string stepHighlightBgPost: "#ebd35b"
            property string stepHighlightBorder: "#800000"

            property string stepEvenIdxBg: "#f2f2f2"
            property string stepOddIdxBg: "#f9f9f9"
            property string stepInactiveBorder: "transparent"

            property string stepOperatorTxt: "#002060"

            property string stepHighlightBg: inPostNode ? stepHighlightBgPre : stepHighlightBgPost
            property string stepInactiveBg: index % 2 == 0 ? stepEvenIdxBg : stepOddIdxBg

            id: wrapper
            width: proceduresList.width
            height: procedureColumn.height + 10
            color: ListView.isCurrentItem ? stepHighlightBg : stepInactiveBg
            border.color: ListView.isCurrentItem ? stepHighlightBorder : stepInactiveBorder

            Column {
                id: procedureColumn
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 10
                anchors.rightMargin: 10

                RowLayout {
                    id: stepRow
                    width: proceduresList.width

                    Text {
                        text: index + 1 + "."
                        font.weight: Font.Bold
                        font.pointSize: 11
                        Layout.alignment: Qt.AlignTop
                    }

                    Text {
                        text: operator + ":"
                        color: stepOperatorTxt
                        font.weight: Font.Bold
                        font.pointSize: 11
                        Layout.alignment: Qt.AlignTop
                    }

                    Text {
                        text: action
                        font.weight: wrapper.ListView.isCurrentItem ? Font.Bold : Font.Normal
                        font.pointSize: 11
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignTop
                    }
                }

                // TODO(jacob): Do we really need a Loader here, or can we just insert the Repeater
                // directly?
                Loader {
                    property bool isActive: wrapper.ListView.isCurrentItem && inPostNode

                    visible: isActive
                    sourceComponent: isActive ? stepConditionsDelegate : null
                    onStatusChanged: if (status == Loader.Ready) item.model = conditions
                }
            }
        }
    }

    Component {
        id: stepConditionsDelegate

        Column {
            property alias model : conditionRepeater.model

            Rectangle {
                height: 5
                width: proceduresList.width
                color: "transparent"
            }

            Repeater {
                id: conditionRepeater

                delegate: Rectangle {
                    height: 30
                    width: proceduresList.width
                    color: "transparent"

                    Text {
                        property string condSatisfiedTxt: "#005000"
                        property string condNotSatisfiedTxt: "#4d4d4d"

                        // TODO(jacob): Figure out how to get this text to wrap
                        anchors.verticalCenter: parent.verticalCenter
                        x: 30
                        font.pointSize: 10
                        font.weight: modelData.satisfied ? Font.Bold : Font.Normal
                        color: modelData.satisfied ? condSatisfiedTxt : condNotSatisfiedTxt
                        text: "[" + modelData.condition + "] " + modelData.transition
                    }
                }
            }
        }
    }

    Rectangle {
        property string procFooterBg: "#007700"

        Layout.alignment: Qt.AlignBottom
        Layout.minimumHeight: 100
        Layout.preferredHeight: 100
        Layout.fillWidth: true
        color: procFooterBg

        RowLayout {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter

            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/play_backwards.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.procPlayBackwards()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/undo.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.procUndo()
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
                        proceduresBridge.procPlay()
                    } else {
                        proceduresBridge.procPause()
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

                onClicked: proceduresBridge.procStop()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/step_forward.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.procStepForward()
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                icon.source: "themes/default/advance.png"
                icon.color: "transparent"

                onClicked: proceduresBridge.procAdvance()
            }
        }
    }

    Rectangle {
        property string procFooterBg: "#007700"

        Layout.alignment: Qt.AlignBottom
        Layout.minimumHeight: 100
        Layout.preferredHeight: 100
        Layout.fillWidth: true
        color: procFooterBg

        RowLayout {
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            TextField {
                id: stepInput
                width: 50
                text: "0"
            }
            Button {
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 50
                Layout.preferredWidth: 50
                text: "Jump"

                onClicked: proceduresBridge.procJump(stepInput.text)
            }
        }
    }
}
