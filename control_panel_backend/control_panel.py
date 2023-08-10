# Copyright (C) 2023, NG:ITL
import os
import sys
import json
import pynng

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QTimer
from PySide6.QtCore import QSocketNotifier

from control_panel_backend.control_panel_model import ControlPanelModel

CONTROL_PANEL_PYNNG_ADDRESS = "ipc:///tmp/RAAI/control_panel.ipc"
CONTROL_COMPONENT_PYNNG_ADDRESS = "ipc:///tmp/RAAI/vehicle_output_writer.ipc"
PLATFORM_CONTROLLER_PYNNG_ADDRESS = "ipc:///tmp/RAAI/driver_input_reader.ipc"


def send_data(pub: pynng.Pub0, payload: dict, topic: str = " ", p_print: bool = True) -> None:
    """
    publishes data via pynng

    :param pub: publisher
    :param payload: data that should be sent in form of a dictionary
    :param topic: the topic under which the data should be published  (e.g. "lap_time:")
    :param p_print: if true, the message that is sent will be printed out. Standard is set to true
    """
    json_data = json.dumps(payload)
    topic = topic + " "
    msg = topic + json_data
    if p_print is True:
        print(f"data send: {msg}")
    pub.send(msg.encode())


def receive_data(sub: pynng.Sub0) -> dict:
    """
    receives data via pynng and returns a variable that stores the content

    :param sub: subscriber
    :param timer: timeout timer for max waiting time for new signal
    """
    msg = sub.recv()
    data = remove_pynng_topic(msg)
    data = json.loads(data)
    return data


def remove_pynng_topic(data, sign: str = " ") -> str:
    """
    removes the topic from data that got received via pynng and returns a variable that stores the content

    :param data: date received from subscriber
    :param sign: last digit from the topic
    """
    decoded_data: str = data.decode()
    i = decoded_data.find(sign)
    decoded_data = decoded_data[i + 1:]
    return decoded_data


def read_config(config_file_path: str) -> dict:
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as file:
            return json.load(file)
    else:
        return create_config(config_file_path)


def create_config(config_file_path: str) -> dict:
    """wrote this to ensure that a config file always exists, ports have to be adjusted if necessary"""
    print("No Config File found, creating new one from Template")
    print("---!Using default argments for a Config file")
    template = {
        "max_throttle": 15,
        "max_brake": 50,
        "max_clutch": 50,
        "max_steering": 100,
        "button_status": False,
        "platform_status": True,
        "pedal_status": True,
        "head_tracking_status": False,
        "steering_offset": -8.0
    }

    file = json.dumps(template, indent=4)
    with open(config_file_path, 'w') as f:
        f.write(file)

    return template


def resource_path() -> Path:
    base_path = getattr(sys, "_MEIPASS", os.getcwd())
    return Path(base_path)


class ControlPanel:

    def __init__(self, config_file_path='./control_panel_config.json') -> None:

        self.config = read_config(config_file_path)

        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        self.control_panel_model = ControlPanelModel()
        self.engine.rootContext().setContextProperty("control_panel_model", self.control_panel_model)
        # and load the QML panel
        self.engine.load(resource_path() / "frontend/qml/main.qml")

        # connect to the signals from the QML file
        self.engine.rootObjects()[0].sliderMaxThrottleChanged.connect(self.control_panel_model.set_max_throttle)
        self.engine.rootObjects()[0].sliderMaxBrakeChanged.connect(self.control_panel_model.set_max_brake)
        self.engine.rootObjects()[0].sliderMaxClutchChanged.connect(self.control_panel_model.set_max_clutch)
        self.engine.rootObjects()[0].sliderMaxSteeringChanged.connect(self.control_panel_model.set_max_steering)
        self.engine.rootObjects()[0].sliderAllMaxSpeedChanged.connect(self.control_panel_model.set_all_speed_max)

        self.engine.rootObjects()[0].sliderSteeringOffsetChanged.connect(self.control_panel_model.set_steering_offset)

        self.engine.rootObjects()[0].buttonResetHeadTracking.connect(self.handle_head_tracker_reset_request)

        self.engine.rootObjects()[0].buttonButtonStatusChanged.connect(self.control_panel_model.change_button_status)
        self.engine.rootObjects()[0].buttonPlatformStatusChanged.connect(self.change_platform_status)
        self.engine.rootObjects()[0].buttonPedalStatusChanged.connect(self.control_panel_model.change_pedal_status)
        self.engine.rootObjects()[0].buttonHeadTrackingChanged.connect(self.control_panel_model.change_head_tracking_status)

        self.engine.rootObjects()[0].timerStart.connect(self.timer_start)
        self.engine.rootObjects()[0].timerPause.connect(self.timer_pause)
        self.engine.rootObjects()[0].timerStop.connect(self.timer_stop)
        self.engine.rootObjects()[0].timerReset.connect(self.timer_reset)
        self.engine.rootObjects()[0].timerResetFull.connect(self.timer_reset_full)
        self.engine.rootObjects()[0].timerIgnore.connect(self.timer_ignore)

        self.driver_input_timer = QTimer()
        self.driver_input_timer.timeout.connect(self.send_driver_throttle_data)
        self.driver_input_timer.start(1)

        self.control_panel_model.set_steering_offset(self.config["steering_offset"])

        self.control_panel_model.set_max_throttle(self.config["max_throttle"])
        self.control_panel_model.set_max_brake(self.config["max_brake"])
        self.control_panel_model.set_max_clutch(self.config["max_clutch"])
        self.control_panel_model.set_max_steering(self.config["max_steering"])

        self.control_panel_model.set_button_status(self.config["button_status"])
        self.control_panel_model.set_platform_status(self.config["platform_status"])
        self.control_panel_model.set_pedal_status(self.config["pedal_status"])
        self.control_panel_model.set_head_tracking_status(self.config["head_tracking_status"])

        self.sent_center_request = False

        self.max_throttle = self.control_panel_model.get_max_throttle()
        self.max_brake = self.control_panel_model.get_max_brake()
        self.max_clutch = self.control_panel_model.get_max_clutch()

        self.max_steering = self.control_panel_model.get_max_steering()
        self.steering_offset = self.control_panel_model.get_steering_offset()


        sending_address = self.config["pynng"]["publishers"]["__pynng_data_publisher"]["address"]
        self.__pynng_data_publisher = pynng.Pub0()
        self.__pynng_data_publisher.listen(sending_address)

        receiving_address = self.config["pynng"]["subscribers"]["__driver_input_receiver"]["address"]
        receiving_topic = self.config["pynng"]["subscribers"]["__driver_input_receiver"]["topics"]["driver_input"]
        self.__driver_input_receiver = pynng.Sub0()
        self.__driver_input_receiver.subscribe(receiving_topic)
        self.__driver_input_receiver.dial(receiving_address, block=False)
        self._notifier = QSocketNotifier(self.__driver_input_receiver.recv_fd, QSocketNotifier.Read)
        self._notifier.activated.connect(self.handle_driver_input)

    def handle_head_tracker_reset_request(self) -> None:
        pass

    def send_driver_throttle_data(self) -> None:
        # self.control_panel_model.set_actual_all(0, 0, 0, steering_percent)
        # self.control_panel_model.set_all(0, 0, 0, steering_percent_scaled)
        self.max_throttle = self.control_panel_model.get_max_throttle()
        self.max_brake = self.control_panel_model.get_max_brake()
        self.max_clutch = self.control_panel_model.get_max_clutch()

        self.max_steering = self.control_panel_model.get_max_steering()
        self.steering_offset = self.control_panel_model.get_steering_offset()

        throttle_payload = {
            "throttle": 0,
            "brake": 0,
            "clutch": 0,
            "steering": self.max_steering,
            "steering_offset": self.steering_offset
        }

        if self.control_panel_model.get_pedal_status():
            throttle_payload = {
                "max_throttle": self.max_throttle,
                "max_brake": self.max_brake,
                "max_clutch": self.max_clutch,
                "max_steering": self.max_steering,
                "steering_offset": self.steering_offset
            }

        config_topic = self.config["pynng"]["publishers"]["__pynng_data_publisher"]["topics"]["config"]
        send_data(self.__pynng_data_publisher, throttle_payload, config_topic, p_print=False)

    def handle_driver_input(self) -> None:
        driver_payload = receive_data(self.__driver_input_receiver)

        throttle = driver_payload["throttle"]
        brake = driver_payload["brake"]
        clutch = driver_payload["clutch"]
        steering = driver_payload["steering"]
        tilt_x = driver_payload["tilt_x"]
        tilt_y = driver_payload["tilt_y"]
        vibration = driver_payload["vibration"]
        # print(brake)
        self.control_panel_model.set_actual_all(throttle, brake, clutch, steering)

        self.max_throttle = self.control_panel_model.get_max_throttle()
        self.max_brake = self.control_panel_model.get_max_brake()
        self.max_clutch = self.control_panel_model.get_max_clutch()
        self.max_steering = self.control_panel_model.get_max_steering()

        throttle_scaled = throttle * (self.max_throttle/100)
        brake_scaled = brake * (self.max_brake/100)
        clutch_scaled = clutch * (self.max_clutch/100)
        steering_scaled = steering * (self.max_steering/100)

        self.control_panel_model.set_all(throttle_scaled, brake_scaled, clutch_scaled, steering_scaled)

    def start(self):
        self.app.exec()

        print("exiting control panel")

    # timer is listening to specified port
    # used for links in buttons
    def send_to_timer(self, string: str, topic: str) -> None:
        # self.__pub.send(string.encode())
        payload = {"signal": string}
        send_data(self.__pynng_data_publisher, payload, topic)

    def timer_start(self) -> None:
        self.send_to_timer("start", "timer_signal")

    def timer_pause(self) -> None:
        self.send_to_timer("pause", "timer_signal")

    def timer_stop(self) -> None:
        self.send_to_timer("stop", "timer_signal")

    def timer_reset(self) -> None:
        self.send_to_timer("reset", "timer_signal")

    def timer_reset_full(self) -> None:
        self.send_to_timer("reset full", "timer_signal")

    def timer_ignore(self) -> None:
        self.send_to_timer("ignore", "timer_signal")

    def change_platform_status(self) -> None:
        self.control_panel_model.set_platform_status(not self.control_panel_model.get_platform_status())
        self.send_platform_signal()

    def send_platform_signal(self) -> None:
        payload = {"platform_status": self.control_panel_model.get_platform_status()}
        platform_topic = self.config["pynng"]["publishers"]["__pynng_data_publisher"]["topics"]["platform"]
        send_data(self.__pynng_data_publisher, payload, platform_topic)
