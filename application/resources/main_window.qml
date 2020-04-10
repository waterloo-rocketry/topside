import QtQuick 2.0

import QtQuick.Layouts 1.12
import QtQuick.Controls 2.13
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

import Qt.labs.settings 1.0

ApplicationWindow {
    id: main_window
    width: 1200
    height: 800
    title: "Operations Simulator"
    visible: true
    visibility: Window.Maximized

    // TODO(jacob): Save and restore window dimensions as well as SplitView dimensions.

    Component.onCompleted: {
        vertical_split.restoreState(settings.vertical_split_state)
        horizontal_split.restoreState(settings.horizontal_split_state)
    }

    Component.onDestruction: {
        settings.vertical_split_state = vertical_split.saveState()
        settings.horizontal_split_state = horizontal_split.saveState()
    }

    Settings {
        id: settings
        property var vertical_split_state
        property var horizontal_split_state
    }

    SplitView {
        id: vertical_split
        anchors.fill: parent
        orientation: Qt.Vertical
        
        SplitView {
            id: horizontal_split
            orientation: Qt.Horizontal
            SplitView.minimumHeight: 600
            SplitView.fillHeight: true

            Rectangle {
                id: daq_pane
                SplitView.minimumWidth: 200
                SplitView.preferredWidth: 400
                color: "green"
            }

            Rectangle {
                id: plumbing_pane
                SplitView.minimumWidth: 800
                SplitView.fillWidth: true
                color: "blue"
            }

            Rectangle {
                id: procedures_pane
                SplitView.minimumWidth: 200
                SplitView.preferredWidth: 400
                color: "purple"
            }
        }

        Rectangle {
            id: controls_pane
            SplitView.minimumHeight: 200
            SplitView.preferredHeight: 400
            color: "red"
        }
    }
}
