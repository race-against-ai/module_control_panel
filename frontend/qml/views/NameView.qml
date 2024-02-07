import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "./../items"

Item {
    signal navigateBack()

    anchors.fill: parent

    Rectangle {
        id: background
        anchors.fill: parent
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {
                position: 0.0
                color: background_color_start_light
            }
            GradientStop {
                position: 1.0
                color: background_color_stop_light
            }
        }
        Component.onCompleted: {
            console.log("Background created");
        }
    }

    Image {
        id: vw_logo
        source: "./../pictures/ui_Background_VW_logo.svg"
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        height: parent.height
        width: parent.width
        scale: 0.9
    }

    Image {
        id: ngitl_logo
        source: "./../pictures/ui_Background_NGITL_logo_logo.svg"
        anchors.fill: parent
    }


    Text {
        text: "Race Against AI"
        y: 10
        x: parent.width / 2 - width / 2
        color: caption_text_color
        font.pointSize: parent.height / 15
        font.bold: true
    }

    TextField {
            id: nameInputField
            width: parent.width / 2
            font.pointSize: parent.height / 15
            anchors.centerIn: parent
            placeholderText: "Namen eingeben"
    }

    VariousButton {
        text: "Send Name"
        width: parent.width * 0.2
        height: parent.height / 10
        anchors.top: nameInputField.bottom
        anchors.horizontalCenter: parent.horizontalCenter

        onClicked: {
            window.onNameChanged(nameInputField.text)
            nameInputField.text = ""
        }
    }
}