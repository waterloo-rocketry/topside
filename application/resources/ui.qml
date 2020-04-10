import QtQuick 2.0
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.13
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: main_window
    width: 1200
    height: 800
    title: "Operations Simulator"
    visible: true

    SplitView {
        anchors.fill: parent
        orientation: Qt.Vertical
        
        SplitView {
            orientation: Qt.Horizontal
            SplitView.minimumHeight: 600
            SplitView.fillHeight: true

            Rectangle {
                id: daq_pane
                SplitView.minimumWidth: 200
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
                color: "purple"
            }
        }

        Rectangle {
            id: controls_pane
            SplitView.minimumHeight: 200
            color: "red"
        }
    }
}
