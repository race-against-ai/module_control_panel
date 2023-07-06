import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "./items"

Window {
	id: window

	width: 1000
	height: 540
	
	visible: true
    visibility: "FullScreen"
	title: qsTr("race against ai - control panel")

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
    property bool isFullScreen: true
	
	// VW colours for the bars
	property string barForeground: "#3BD8DD"
	property string barBackground: "#226F78"
	property string controlBackground: "#5F95AF"
	
	// height of every bar (for showing the values)
    property int barHeight: 60
	
	// size of the fonts
	property int fontNumberSize: 30
	property int fontDescriptionSize: 18
	property int fontSliderSize: 14
	
	
	// style of the numbers
	// numbers after the comma
	property int postComma: 2
	// complete length of all numbers (e.g.: value is 6; "12.34" will be changed to " 12.34")
	property int numLength: 6
	
	// all controls (throttle, brake, clutch, and steering wheel) have two rectangles:
	// the first one is for the actual value
	// the second is for the used value

	// since signals can't be a property all of the controls have to be in a single file
	Rectangle {
		id: backgroundRectangle

		anchors.fill: parent
		color: "#00354D"

		ColumnLayout {
			id: columnLayout

			anchors.fill: parent
            spacing: 5

			SteeringControl {
				id: steeringControl

                height: 125
				Layout.fillWidth: true
				Layout.leftMargin: 15
				Layout.rightMargin: 15
				Layout.topMargin: 15

				color: controlBackground
				barBackground: window.barBackground
				barForeground: window.barForeground

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

			PedalControl {
				id: throttlePedalControl

                height: 85
				Layout.fillWidth: true
				Layout.leftMargin: 15
				Layout.rightMargin: 15

				title: "throttle"

				color: controlBackground
				barBackground: window.barBackground
				barForeground: window.barForeground

				value: control_panel_model.throttle
				actualValue: control_panel_model.actual_throttle
                maxValue: control_panel_model.max_throttle

                onSliderMaxChanged: function(val) {
                    window.sliderMaxThrottleChanged(val)
				}
			}

			PedalControl {
				id: brakePedalControl

                height: 85
				Layout.fillWidth: true
				Layout.leftMargin: 15
				Layout.rightMargin: 15

				title: "break"

				color: controlBackground
				barBackground: window.barBackground
				barForeground: window.barForeground

				value: control_panel_model.brake
				actualValue: control_panel_model.actual_brake
				maxValue: control_panel_model.max_brake

                onSliderMaxChanged: function(val) {
                    sliderMaxBrakeChanged(val)
				}
			}

			PedalControl {
				id: clutchPedalControl

                height: 85
				Layout.fillWidth: true
				Layout.leftMargin: 15
				Layout.rightMargin: 15


				title: "Clutch"

				color: controlBackground
				barBackground: window.barBackground
				barForeground: window.barForeground

				value: control_panel_model.clutch
				actualValue: control_panel_model.actual_clutch
				maxValue: control_panel_model.max_clutch

                onSliderMaxChanged: function(val) {
                    sliderMaxClutchChanged(val)
				}
			}

			// controls all pedals at the same time
			Rectangle {
				id: overallPedalControl

				height: 50
				Layout.fillWidth: true
				Layout.leftMargin: 15
				Layout.rightMargin: 15
				color: controlBackground

				Slider {
					x: 10
					y: 10
					height: 40
					width: parent.width - 20

					from: 0
					to: 100
					value: control_panel_model.all_speed_max

                    onMoved: sliderAllMaxSpeedChanged(value)

					Text {
						y: -10
						text: parent.value.toFixed(2) + "%"
						anchors.horizontalCenter: parent.horizontalCenter
						font.family: "Consolas"
						font.bold: true
						font.pointSize: fontSliderSize
					}
				}
            }

            VariousButtonRow {
                Layout.fillWidth: true
                Layout.leftMargin: 15
                Layout.rightMargin: 15
            }

            TimerControlButtons {
                Layout.fillWidth: true
                Layout.leftMargin: 15
                Layout.rightMargin: 15
            }

		}

	}
}
