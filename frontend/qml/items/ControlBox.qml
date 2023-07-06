import QtQuick 2.0
import QtQuick.Controls 2.15

Item {
    Rectangle {
        radius: 20
        color: window.light_grey
        height: parent.height
        width: parent.width
        border.color: "white"
        border.width: 5

        Text {
            id: control
            text: "Control"
            color: window.dark_blue_text_color
            font.bold: true
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.height * 0.01
            font.pointSize: parent.width * 0.15
        }

        Item {
            id: container
            width: parent.width
            height: parent.height * 0.6
            anchors.verticalCenter: parent.verticalCenter

            VariousSwitch {
                y: 0
                x: container.width / 2 - width / 2
                text: "BTN"
                checked: true

                onClicked: function() {
                    buttonButtonStatusChanged()
                }

                Text {
                    text: "BTN"
                    font.pixelSize: container.height / 20
                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

            VariousSwitch {
                y: parent.height * 1 / 5
                x: container.width / 2 - width / 2
                text: "Pedals"
                checked: true

                onClicked: function() {
                    buttonPedalStatusChanged()
                }

                Text {
                    text: "Pedals"
                    font.pixelSize: container.height / 20
                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

            VariousSwitch {
                y: parent.height * 2 / 5
                x: container.width / 2 - width / 2
                text: "HT"

                onClicked: function() {
                    buttonHeadTrackingChanged()
                }

                Text {
                    text: "HT"
                    font.pixelSize: container.height / 20;                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

            VariousSwitch {
                y: parent.height * 3 / 5
                x: container.width / 2 - width / 2
                text: "HT Reset"
                checked: true

                onClicked: function() {
                    buttonResetHeadTracking()
                }

                Text {
                    text: "HT Reset"
                    font.pixelSize: container.height / 20
                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

            VariousSwitch {
                y: parent.height * 4 / 5
                x: container.width / 2 - width / 2
                text: "Platform"
                checked: true

                onClicked: function() {
                    buttonPlatformStatusChanged()
                }

                Text {
                    text: "Platform"
                    font.pixelSize: container.height / 20
                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

            VariousSwitch {
                y: parent.height * 5 / 5
                x: container.width / 2 - width / 2

                onClicked: function() {
                    isFullScreen = ! isFullScreen

                    if(isFullScreen) {
                        window.visibility = "FullScreen"
                    }
                    else {
                        window.visibility = "Windowed"
                    }
                }

                Text {
                    text: "Fullscreen"
                    font.pixelSize: container.height / 20
                    color: control.down ? "black" : window.dark_blue_text_color
                    x: parent.width / 2 - width / 2
                    anchors.top: parent.bottom
                }
            }

        }
    }
}
