import QtQuick 2.14

import QtQuick.Layouts 1.12
import QtQuick.Controls 2.13
import QtQuick.Window 2.12

import Qt.labs.settings 1.0

ApplicationWindow {
    id: mainWindow
    width: 1200
    height: 800
    title: "Operations Simulator"
    visible: true
    visibility: Window.Maximized

    menuBar: MenuBar {
        Menu {
            title: "&File"

            Action {
                text: "&Quit"
                shortcut: StandardKey.Quit
                onTriggered: mainWindow.close()
            }
        }
    }

    // TODO(jacob): Save and restore window dimensions as well as SplitView dimensions.

    Component.onCompleted: {
        verticalSplit.restoreState(settings.verticalSplitState)
        horizontalSplit.restoreState(settings.horizontalSplitState)
    }

    Component.onDestruction: {
        settings.verticalSplitState = verticalSplit.saveState()
        settings.horizontalSplitState = horizontalSplit.saveState()
    }

    Settings {
        id: settings
        property var verticalSplitState
        property var horizontalSplitState
    }

    SplitView {
        id: verticalSplit
        anchors.fill: parent
        orientation: Qt.Vertical
        
        SplitView {
            id: horizontalSplit
            orientation: Qt.Horizontal
            SplitView.preferredHeight: 600
            SplitView.fillHeight: true
            Layout.margins: 10

            DAQPane {
                id: daqPane
                // SplitView.minimumWidth: 200
                SplitView.preferredWidth: 400
            }

            PlumbingPane {
                id: plumbingPane
                SplitView.preferredWidth: 800
                SplitView.fillWidth: true
            }

            ProceduresPane {
                id: proceduresPane
                // SplitView.minimumWidth: 200
                SplitView.preferredWidth: 400
                Layout.margins: 10
            }
        }

        ControlsPane {
            id: controlsPane
            // SplitView.minimumHeight: 200
            SplitView.preferredHeight: 400
        }
    }
}
