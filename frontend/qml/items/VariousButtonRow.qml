import QtQuick 2.15
import QtQuick.Controls 2.15

// various controls
Rectangle {
    height: 40
    color: controlBackground

    // used for changing the window state    
    ButtonWithBackground {
        x: 0
        y: 0
        height: 40
        width: 210

        buttonText: isFullScreen ? "FullScreen" : "Windowed"
        externalActivity: isFullScreen
        useExternalActivity: true

        onButtonClicked: function() {
            isFullScreen = !isFullScreen

            if(isFullScreen) {
                window.visibility = "FullScreen"
            } else {
                window.visibility = "Windowed"
            }
        }
    }

    // disable or enable buttons on the steering wheel
    ButtonWithBackground {
        x: 210
        y: 0
        height: 40
        width: 210

        buttonText: control_panel_model.button_status ? "BTN active" : "BTN inactive"
        externalActivity: control_panel_model.button_status
        useExternalActivity: true

        onButtonClicked: function() {
            buttonButtonStatusChanged()
        }
    }

    // enable or disable the platform
    ButtonWithBackground {
        x: 420
        y: 0
        height: 40
        width: 210

        buttonText: control_panel_model.platform_status ? "platform active" : "platform inactive"
        externalActivity: control_panel_model.platform_status
        useExternalActivity: true

        onButtonClicked: function() {
            buttonPlatformStatusChanged()
        }
    }

    ButtonWithBackground {
        x: 630
        y: 0
        height: 40
        width: 210

        buttonText: control_panel_model.pedal_status ? "pedals active" : "pedals inactive"
        externalActivity: control_panel_model.pedal_status
        useExternalActivity: true

        onButtonClicked: function() {
            buttonPedalStatusChanged()
        }
    }

    ButtonWithBackground {
        x: 840
        y: 0
        height: 40
        width: 210

        buttonText: "reset HT"
        invertActivity: true

        onButtonClicked: function() {
            buttonResetHeadTracking()
        }
    }

    ButtonWithBackground {
        x: 1050
        y: 0
        height: 40
        width: 210

        buttonText: control_panel_model.head_tracking_status ? "HT active" : "HT inactive"
        externalActivity: control_panel_model.head_tracking_status
        useExternalActivity: true

        onButtonClicked: function() {
            buttonHeadTrackingChanged()
        }
    }
}
