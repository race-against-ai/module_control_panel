# Copyright (C) 2023, NG:ITL
import os
import sys
import json
import pynng
import time

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QTimer
from PySide6.QtCore import QSocketNotifier

from control_panel_backend.control_panel_model import ControlPanelModel
from control_panel_backend.timer_model import Timer
from control_panel_backend.database_interface_model import DriverDataPublisher
from enum import IntEnum

CONTROL_PANEL_PYNNG_ADDRESS = "ipc:///tmp/RAAI/control_panel.ipc"
CONTROL_COMPONENT_PYNNG_ADDRESS = "ipc:///tmp/RAAI/vehicle_output_writer.ipc"
PLATFORM_CONTROLLER_PYNNG_ADDRESS = "ipc:///tmp/RAAI/driver_input_reader.ipc"
SESSION_STATUS_RECEIVER_ADDRESS = "ipc:///tmp/RAAI/session_status.ipc"


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


def receive_data(sub: pynng.Sub0):
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
    decoded_data = decoded_data[i + 1 :]
    return decoded_data


def read_config(config_file_path: str) -> dict:
    if os.path.isfile(config_file_path):
        with open(config_file_path, "r") as file:
            return json.load(file)
    else:
        return create_config(config_file_path)


def create_config(config_file_path: str) -> dict:
    """wrote this to ensure that a config file always exists, ports have to be adjusted if necessary"""
    print("No Config File found, creating new one from Template")
    print("---!Using default argments for a Config file")
    template = {
        "pynng": {
            "publishers": {
                "__pynng_data_publisher": {
                    "address": "ipc:///tmp/RAAI/control_panel.ipc",
                    "topics": {
                        "platform": "platform",
                        "config": "config"
                    }
                }
            },
            "subscribers": {
                "__driver_input_receiver": {
                    "address": "ipc:///tmp/RAAI/driver_input_reader.ipc",
                    "topics": {
                        "driver_input": "driver_input"
                    }
                }
            }
        },
        "max_throttle": 15,
        "max_brake": 50,
        "max_clutch": 50,
        "max_steering": 100,
        "button_status": False,
        "platform_status": True,
        "pedal_status": True,
        "head_tracking_status": False,
        "steering_offset": -8.0,
    }

    file = json.dumps(template, indent=4)
    with open(config_file_path, "w") as f:
        f.write(file)

    return template


def resource_path() -> Path:
    base_path = getattr(sys, "_MEIPASS", os.getcwd())
    return Path(base_path)


class TimerStates(IntEnum):
    RESET = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3


class ControlPanel:
    def __init__(self, config_file_path="./control_panel_config.json") -> None:
        self.config = read_config(config_file_path)

        self.start_timestamp_ns = time.time_ns()
        self.diff = 0
        self.t_model = Timer(0, 0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_callback)  # type: ignore

        self.database_model = DriverDataPublisher(
            self.config["pynng"]["publishers"]["name_publisher"]["address"],
            self.config["pynng"]["requesters"]["database_request"]["address"],
        )

        self.timer_state = 0

        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        self.control_panel_model = ControlPanelModel()
        self.engine.rootContext().setContextProperty("control_panel_model", self.control_panel_model)
        self.engine.rootContext().setContextProperty("t_model", self.t_model)
        # and load the QML panel
        self.engine.load(resource_path() / "frontend/qml/main.qml")

        self.engine.rootContext().setContextProperty("t_model", self.t_model)
        self.engine.rootContext().setContextProperty("database_model", self.database_model)

        # connect to the signals from the QML file
        self.engine.rootObjects()[0].sliderMaxThrottleChanged.connect(self.control_panel_model.set_max_throttle)  # type: ignore
        self.engine.rootObjects()[0].sliderMaxBrakeChanged.connect(self.control_panel_model.set_max_brake)  # type: ignore
        self.engine.rootObjects()[0].sliderMaxClutchChanged.connect(self.control_panel_model.set_max_clutch)  # type: ignore
        self.engine.rootObjects()[0].sliderMaxSteeringChanged.connect(self.control_panel_model.set_max_steering)  # type: ignore
        self.engine.rootObjects()[0].sliderAllMaxSpeedChanged.connect(self.control_panel_model.set_all_speed_max)  # type: ignore

        self.engine.rootObjects()[0].sliderSteeringOffsetChanged.connect(self.control_panel_model.set_steering_offset)  # type: ignore

        self.engine.rootObjects()[0].buttonResetHeadTracking.connect(self.handle_head_tracker_reset_request)  # type: ignore

        self.engine.rootObjects()[0].buttonButtonStatusChanged.connect(self.control_panel_model.change_button_status)  # type: ignore
        self.engine.rootObjects()[0].buttonPlatformStatusChanged.connect(self.change_platform_status)  # type: ignore
        self.engine.rootObjects()[0].buttonPedalStatusChanged.connect(self.control_panel_model.change_pedal_status)  # type: ignore
        self.engine.rootObjects()[0].buttonHeadTrackingChanged.connect(  # type: ignore
            self.control_panel_model.change_head_tracking_status
        )

        self.engine.rootObjects()[0].timerStart.connect(self.timer_start)  # type: ignore
        self.engine.rootObjects()[0].timerPause.connect(self.timer_pause)  # type: ignore
        self.engine.rootObjects()[0].timerStop.connect(self.timer_stop)  # type: ignore
        self.engine.rootObjects()[0].timerReset.connect(self.timer_reset)  # type: ignore
        self.engine.rootObjects()[0].timerResetFull.connect(self.timer_reset_full)  # type: ignore
        self.engine.rootObjects()[0].timerIgnore.connect(self.timer_ignore)  # type: ignore

        self.driver_input_timer = QTimer()
        self.driver_input_timer.timeout.connect(self.send_driver_throttle_data)  # type: ignore
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
        self._notifier.activated.connect(self.handle_driver_input)  # type: ignore

    def timer_callback(self) -> None:
        current_timestamp_ns = time.time_ns()
        self.diff = current_timestamp_ns - self.start_timestamp_ns
        self.t_model.set_timestamp(self.diff)

        self.__session_receiver = pynng.Sub0()
        self.__session_receiver.subscribe("")
        self.__session_receiver.dial(SESSION_STATUS_RECEIVER_ADDRESS, block=False)

        self.session_receiver_socket_notifier = QSocketNotifier(self.__session_receiver.recv_fd, QSocketNotifier.Read)
        self.session_receiver_socket_notifier.activated.connect(self.handle_session_status)

    def timer_callback(self) -> None:
        current_timestamp_ns = time.time_ns()
        self.diff = current_timestamp_ns - self.start_timestamp_ns
        self.t_model.set_timestamp(self.diff)

    def handle_head_tracker_reset_request(self) -> None:
        pass

    def send_driver_throttle_data(self) -> None:
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
            "steering_offset": self.steering_offset,
        }

        if self.control_panel_model.get_pedal_status():
            throttle_payload = {
                "max_throttle": self.max_throttle,
                "max_brake": self.max_brake,
                "max_clutch": self.max_clutch,
                "max_steering": self.max_steering,
                "steering_offset": self.steering_offset,
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

        self.control_panel_model.set_actual_all(throttle, brake, clutch, steering)

        self.max_throttle = self.control_panel_model.get_max_throttle()
        self.max_brake = self.control_panel_model.get_max_brake()
        self.max_clutch = self.control_panel_model.get_max_clutch()
        self.max_steering = self.control_panel_model.get_max_steering()

        throttle_scaled = throttle * (self.max_throttle / 100)
        brake_scaled = brake * (self.max_brake / 100)
        clutch_scaled = clutch * (self.max_clutch / 100)
        steering_scaled = steering * (self.max_steering / 100)

        self.control_panel_model.set_all(throttle_scaled, brake_scaled, clutch_scaled, steering_scaled)

    def handle_session_status(self):
        session_payload = receive_data(self.__session_receiver)
        print(session_payload)
        if session_payload["Session_status"] == "Start":
            self.control_panel_model.set_pedal_status(True)
            self.timer_reset()
            self.timer_start()
        else:
            self.control_panel_model.set_pedal_status(False)
            self.timer_stop()
        print(self.control_panel_model.pedal_status)

    def start(self):
        self.app.exec()

        print("exiting control panel")

    # timer is listening to specified port
    # used for links in buttons
    def send_to_timer(self, string: str, topic: str) -> None:
        """
        Sends a message to the timer.

        Args:
        string (str): The message to send.
        topic (str): The topic to send the message on.
        """

        payload = {"signal": string}
        send_data(self.__pynng_data_publisher, payload, topic)

    def timer_start(self) -> None:
        if self.timer_state == TimerStates.STOPPED:
            self.diff = 0
            self.t_model.set_timestamp(0)

        self.start_timestamp_ns = time.time_ns() - self.diff
        self.timer.start()
        self.timer_state = TimerStates.RUNNING

    def timer_pause(self) -> None:
        if self.timer_state == TimerStates.PAUSED:
            self.start()
        else:
            self.timer.stop()
            self.timer_state = TimerStates.PAUSED

    def timer_stop(self) -> None:
        if self.timer_state == TimerStates.PAUSED:
            self.start()
        else:
            self.timer.stop()
            self.timer_state = TimerStates.PAUSED

    def timer_reset(self) -> None:
        self.timer.stop()
        self.diff = 0
        self.t_model.set_timestamp(0)
        self.timer_state = TimerStates.RESET

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
