import QtQuick 2.0
import QtQuick.Controls 2.12
import QtQuick.Window 2.12

import VisualizationArea 1.0

Rectangle {

    VisualizationArea {
        id: visualization_area
        color: "black"
        width: parent.width
        height: parent.height
        anchors.centerIn: parent
        Component.onCompleted: test()


        z: 2
    }

    Rectangle {
        id: mouse_controller_area
        anchors.fill: parent
        z: 1


        Component.onCompleted: visualization_area.test()

        Connections {
            target: visualization_area

            onRequest_QML_context: {
                contextMenu.type = type
                contextMenu.popup()

            }

        }

        Menu {
            id: contextMenu

            property var type: "regular"

            onClosed: visualization_area.unfreeze_display()

            MenuItem { 
                text: "Signal to Visualization Area" 
                onClicked: visualization_area.log_from_qml("QML access sucessful!")
            }

            MenuItem {
                text: "Change colors"
                onClicked: {
                    visualization_area.color = "green"
                    visualization_area.force_repaint()
                }
            }

            MenuItem {
                text: "Print global parameters to console"
                onClicked: {
                    visualization_area.print_globals()
                }
            }

            MenuItem {
                text: "Reset zoom"
                onClicked: {
                    visualization_area.reset_all_zoom_and_pan()
                    visualization_area.force_repaint()
                }
            }

            MenuItem {
                text: "Ping node"

                enabled: (contextMenu.type == "node_menu_type")

                onClicked: {
                    visualization_area.log_from_qml("Node pinged!")
                }
            }

            MenuItem {
                text: "Parrot mode!"

                onClicked: {
                    visualization_area.parrot_mode_demo()
                }
            }
        }
    }

    Rectangle {
        id: info_box
        visible: false
        color: "cyan"
        radius: 5
        border.color: "black"
        border.width: 2

        x: 10
        y: 10
        z: 3

        width: 150
        height: 100


        Text {
            id: text_field1
            text: "="
            color: "black"

            x: 15
            y: 20
            z: 4

        }

        Text {
            id: text_field2
            text: "="
            color: "black"

            x: 15
            y: 35
            z: 4

        }

        Connections {
            target: visualization_area

            onRequest_QML_info_box: {
                info_box.visible = true
                text_field1.text = "Node identifier: " + node_data
                text_field2.text = "Node identifier: " + comp_data
            }

            onRetract_QML_info_box_request: info_box.visible = false

        }

    }


    component CustomHoverButtonTemplate : Rectangle {
        property var tooltipText: "Text!"
        property var iconSource: ""
        property var yPosition: 0

        signal pressed()
        signal notifyVisArea()

        id: temp

        x: parent.width - 10 - width
        y: 10 + 35*yPosition
        z: 4

        width: 25
        height: 25

        border.color: "blue"
        border.width: 2

        ToolTip {
            parent: temp
            visible: mouse_hover_controller.containsMouse
            text: tooltipText
        }

        Image {
            id: icon
            source: iconSource

            anchors.centerIn: parent
            width: parent.width - 4
            height: parent.height - 4
        }

        MouseArea {
            id: mouse_hover_controller

            anchors.fill: parent
            hoverEnabled: true


            onClicked: parent.pressed()
        }

    }

    component CustomCheckButton : CustomHoverButtonTemplate {
        property var isChecked: true

        onPressed: {
            isChecked = (!isChecked)
            notifyVisArea()
        }

        Rectangle {
            id: check_cover_rectangle
            anchors.centerIn: parent

            height: parent.height
            width: parent.width

            color: Qt.rgba(0, 0.1, 0.8, 0.2)

            visible: parent.isChecked

        }
    }

    component CustomPressButton : CustomHoverButtonTemplate {

        onPressed: {
            fade_timer.restart()
            press_cover_rectangle.visible = true
            notifyVisArea()
        }

        Rectangle {
            id: press_cover_rectangle
            anchors.centerIn: parent

            height: parent.height
            width: parent.width

            color: Qt.rgba(0, 0.1, 0.8, 0.2)

            visible: false

        }

        Timer {
            id: fade_timer

            interval: 200 
            repeat: false

            onTriggered: {
                press_cover_rectangle.visible = false
            }
        }
    }


    CustomCheckButton {
        tooltipText: "Toggles the grid"
        iconSource: "gui_icons/grid_toggle_icon.png"
        yPosition: 0

        onNotifyVisArea: visualization_area.toggle_grid(isChecked)
    }

    CustomPressButton {
        tooltipText: "Resets the view"
        iconSource: "gui_icons/reset_view_icon.png"
        yPosition: 1

        onNotifyVisArea: { 
            visualization_area.reset_all_zoom_and_pan()
            visualization_area.force_repaint()
        }
    }

    CustomCheckButton {
        tooltipText: "Toggles component visiblity"
        iconSource: "gui_icons/components_visible_icon.png"
        yPosition: 2

        onNotifyVisArea: visualization_area.toggle_component_visibility(isChecked)
    }

    CustomCheckButton {
        tooltipText: "Toggles label visiblity"
        iconSource: "gui_icons/labels_visible_icon.png"
        yPosition: 3

        onNotifyVisArea: visualization_area.toggle_label_visibility(isChecked)
    }

    CustomCheckButton {
        tooltipText: "Toggles image visibility"
        iconSource: "gui_icons/images_visible_icon.png"
        yPosition: 4

        onNotifyVisArea: visualization_area.toggle_image_visibility(isChecked)
    }

}
