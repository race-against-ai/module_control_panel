import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "./items"

Window {
    id: window

    color: "black"
    width: 1280
    height: 720

    minimumHeight: 480
    minimumWidth: 852

    visible: true
    title: qsTr("race against ai - control panel")

    visibility: "Windowed"

    signal sliderMaxThrottleChanged(real value)
    signal sliderMaxBrakeChanged(real value)
    signal sliderMaxClutchChanged(real value)
    signal sliderMaxSteeringChanged(real value)
    signal sliderAllMaxSpeedChanged(real value)

    signal sliderSteeringOffsetChanged(real value)

    signal buttonButtonStatusChanged()
    signal buttonResetHeadTracking()
    signal buttonPedalStatusChanged()
    signal buttonPlatformStatusChanged()
    signal buttonHeadTrackingChanged()

    signal timerStart()
    signal timerPause()
    signal timerStop()
    signal timerReset()
    signal timerResetFull()
    signal timerIgnore()

    // reading window.visibility doesn't return the state (as in "Windowed")
    // this property is needed
    property bool isFullScreen: false



    Image {
        id: background
        //source: "../../assets/ui.svg"
        source: "pictures/ui_Background.svg"
        anchors.fill: parent
    }

    Image {
        id: vw_logo
        source: "pictures/ui_Background_VW_logo.svg"
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        height: parent.height
        width: parent.width
    }

    Image {
        id: car_image
        source: "pictures/ui_car.svg"
        anchors.centerIn: parent
        fillMode: Image.PreserveAspectFit
        height: parent.height
        width: parent.width


    }

    Image {
        id: ngitl_logo
        source: "pictures/ui_Background_NGITL_logo_logo.svg"
        anchors.fill: parent
    }


    Text {
        text: "Race Against AI"
        y: 10
        x: parent.width / 2 - width / 2
        color: "#274c87"
        font.pointSize: parent.height / 15
        font.bold: true
    }

    VerticalSlider {
        id: brake_bar
        text: "brake"
        rotation: -90
        x: parent.width * 0.25
        y: parent.height / 2 - height / 2
        width: parent.width * 0.04
        height: parent.height * 0.7

        value: control_panel_model.brake
        actualValue: control_panel_model.actual_brake
        maxValue: control_panel_model.max_brake

        onSliderMaxChanged: function(val) {
            sliderMaxBrakeChanged(val)
        }
    }

    VerticalSlider {
        id: throttle_bar
        text: "throttle"
        rotation: 90
        x: parent.width * 0.75 - width
        y: parent.height / 2 - height / 2
        width: parent.width * 0.04
        height: parent.height * 0.7

        value: control_panel_model.throttle
        actualValue: control_panel_model.actual_throttle
        maxValue: control_panel_model.max_throttle

        onSliderMaxChanged: function(val) {
            window.sliderMaxThrottleChanged(val)
        }
    }


    ControlBox {
        id: left_setting_box
        height: parent.height * 0.7
        width: parent.width * 0.1
        y: parent.height / 2 - height / 2
        x: parent.width * 0.125
    }

    TimerBox {
        id: right_setting_box
        height: parent.height * 0.7
        width: parent.width * 0.1
        y: parent.height / 2 - height / 2
        x: parent.width * 0.875 - width

    }

    HorizontalSlider {
        id: steering_bar
        width: parent.width * 0.4
        height: parent.width * 0.04
        x: parent.width / 2 - width / 2
        y: parent.height * 0.15

        value: control_panel_model.steering
        actualValue: control_panel_model.actual_steering
        maxValue: control_panel_model.max_steering
        steeringOffset: control_panel_model.steering_offset

        onSliderMaxChanged: function(val) {
            window.sliderMaxSteeringChanged(val)
        }

        onSliderSteeringOffsetChanged: function(val) {
            window.sliderSteeringOffsetChanged(val)
        }
    }

}
