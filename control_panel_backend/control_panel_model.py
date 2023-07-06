# Copyright (C) 2023, NG:ITL
from PySide6.QtCore import QObject, Signal, Property


class ControlPanelModel(QObject):

    def __init__(self) -> None:
        QObject.__init__(self)
        # standard, used for sending
        self._throttle = 0.0
        self._brake = 0.0
        self._clutch = 0.0
        self._steering = 0.0

        # actual, used for processing
        self._actual_throttle = 0.0
        self._actual_brake = 0.0
        self._actual_clutch = 0.0
        self._actual_steering = 0.0

        # max, limits of each value
        self._max_throttle = 100.0
        self._max_brake = 100.0
        self._max_clutch = 100.0
        self._max_steering = 100.0
        self._all_speed_max = 100.0

        # Head tracking
        self._head_tracking_yaw_angle = 0.0

        self._steering_offset = 0.0

        # button activation status, whether the buttons are active
        self._buttons_activated = True
        self._platform_activated = True
        self._pedals_activated = True
        self._head_tracking_activated = True

    # -------------------- set all --------------------
    def set_all(self, throttle: float, brake: float, clutch: float, steering: float) -> None:
        self.set_throttle(throttle)
        self.set_brake(brake)
        self.set_clutch(clutch)
        self.set_steering(steering)

    def set_actual_all(self, throttle: float, brake: float, clutch: float, steering: float) -> None:
        self.set_actual_throttle(throttle)
        self.set_actual_brake(brake)
        self.set_actual_clutch(clutch)
        self.set_actual_steering(steering)

    def set_head_tracking_values(self, yaw_angle: float):
        self.set_head_tracking_yaw_angle(yaw_angle)

    # -------------------- adding values --------------------
    def add_speed_max(self, value: float) -> None:
        if value:
            self.set_all_speed_max(self.get_all_speed_max() + value)

    def add_max_throttle(self, amount: float) -> None:
        self.set_max_throttle(self.get_max_throttle() + amount)

    def add_max_brake(self, amount: float) -> None:
        self.set_max_brake(self._max_brake + amount)

    def add_max_clutch(self, amount: float) -> None:
        self.set_max_clutch(self._max_clutch + amount)

    def add_max_steering(self, amount: float) -> None:
        self.set_max_steering(self._max_steering + amount)

    def add_steering_offset(self, amount: float) -> None:
        self.set_steering_offset(self.get_steering_offset() + amount)

    # ---------- change ----------
    def change_button_status(self) -> None:
        self.set_button_status(not self.get_button_status())

    def change_platform_status(self) -> None:
        self.set_platform_status(not self.get_platform_status())

    def change_pedal_status(self) -> None:
        self.set_pedal_status(not self.get_pedal_status())

    def change_head_tracking_status(self) -> None:
        self.set_head_tracking_status(not self.get_head_tracking_status())

    # -------------------- getters --------------------
    # ---------- standard ----------
    def get_throttle(self) -> float:
        return self._throttle

    def get_brake(self) -> float:
        return self._brake

    def get_clutch(self) -> float:
        return self._clutch

    def get_steering(self) -> float:
        return self._steering

    def get_steering_offset(self) -> float:
        return self._steering_offset

    # ---------- actual values ----------
    def get_actual_throttle(self) -> float:
        return self._actual_throttle

    def get_actual_brake(self) -> float:
        return self._actual_brake

    def get_actual_clutch(self) -> float:
        return self._actual_clutch

    def get_actual_steering(self) -> float:
        return self._actual_steering

    # ---------- max values ----------
    def get_max_throttle(self) -> float:
        return self._max_throttle

    def get_max_brake(self) -> float:
        return self._max_brake

    def get_max_clutch(self) -> float:
        return self._max_clutch

    def get_max_steering(self) -> float:
        return self._max_steering

    def get_all_speed_max(self) -> float:
        return self._all_speed_max

    # ---------- button status ----------
    def get_button_status(self) -> bool:
        return self._buttons_activated

    def get_platform_status(self) -> bool:
        return self._platform_activated

    def get_pedal_status(self) -> bool:
        return self._pedals_activated

    def get_head_tracking_status(self) -> bool:
        return self._head_tracking_activated

    def get_head_tracking_yaw_angle(self) -> float:
        return self._head_tracking_yaw_angle

    # -------------------- setters --------------------
    # ---------- standard ----------
    def set_throttle(self, throttle: float) -> None:
        self._throttle = throttle
        self.throttle_changed.emit()

    def set_brake(self, brake: float) -> None:
        self._brake = brake
        self.brake_changed.emit()

    def set_clutch(self, clutch: float) -> None:
        self._clutch = clutch
        self.clutch_changed.emit()

    def set_steering(self, steering: float) -> None:
        self._steering = steering
        self.steering_changed.emit()

    def set_steering_offset(self, offset: float) -> None:
        self._steering_offset = offset
        self.steering_offset_changed.emit()

    # ---------- actual values ----------
    def set_actual_throttle(self, throttle: float) -> None:
        self._actual_throttle = throttle
        self.actual_throttle_changed.emit()

    def set_actual_brake(self, brake: float) -> None:
        self._actual_brake = brake
        self.actual_brake_changed.emit()

    def set_actual_clutch(self, clutch: float) -> None:
        self._actual_clutch = clutch
        self.actual_clutch_changed.emit()

    def set_actual_steering(self, steering: float) -> None:
        self._actual_steering = steering
        self.actual_steering_changed.emit()

    # ---------- max values ----------
    def set_max_throttle(self, amount: float) -> None:
        self._max_throttle = amount

        if self._max_throttle > 100.0:
            self._max_throttle = 100.0
        if self._max_throttle < 0.0:
            self._max_throttle = 0.0

        self.max_throttle_changed.emit()

    def set_max_brake(self, amount: float) -> None:
        self._max_brake = amount

        if self._max_brake > 100.0:
            self._max_brake = 100.0
        if self._max_brake < 0.0:
            self._max_brake = 0.0

        self.max_brake_changed.emit()

    def set_max_clutch(self, amount: float) -> None:
        self._max_clutch = amount

        if self._max_clutch > 100.0:
            self._max_clutch = 100.0
        if self._max_clutch < 0.0:
            self._max_clutch = 0.0

        self.max_clutch_changed.emit()

    def set_max_steering(self, amount: float) -> None:
        self._max_steering = amount

        if self._max_steering > 200.0:
            self._max_steering = 200.0
        if self._max_steering < 0.0:
            self._max_steering = 0.0

        self.max_steering_changed.emit()

    def set_all_speed_max(self, value: float) -> None:
        self._all_speed_max = value

        if self._all_speed_max > 100.0:
            self._all_speed_max = 100.0
        if self._all_speed_max < 0.0:
            self._all_speed_max = 0.0

        self.set_max_throttle(value)
        self.set_max_brake(value)
        self.set_max_clutch(value)
        self.all_speed_max_changed.emit()

    # ---------- button status ----------
    def set_button_status(self, value: float) -> None:
        self._buttons_activated = value
        self.button_status_changed.emit()

    def set_platform_status(self, value: bool) -> None:
        self._platform_activated = value
        self.platform_status_changed.emit()

    def set_pedal_status(self, value: bool) -> None:
        self._pedals_activated = value
        self.pedal_status_changed.emit()

    def set_head_tracking_status(self, value: bool) -> None:
        self._head_tracking_activated = value
        self.head_tracking_status_changed.emit()

    def set_head_tracking_yaw_angle(self, value: float) -> None:
        self._head_tracking_yaw_angle = value
        self.head_tracking_yaw_angle_changed.emit()

    # -------------------- signals --------------------
    # ---------- standard ----------
    @Signal
    def throttle_changed(self) -> None:
        pass

    @Signal
    def brake_changed(self) -> None:
        pass

    @Signal
    def clutch_changed(self) -> None:
        pass

    @Signal
    def steering_changed(self) -> None:
        pass

    # ---------- actual values ----------
    @Signal
    def actual_throttle_changed(self) -> None:
        pass

    @Signal
    def actual_brake_changed(self) -> None:
        pass

    @Signal
    def actual_clutch_changed(self) -> None:
        pass

    @Signal
    def actual_steering_changed(self) -> None:
        pass

    @Signal
    def steering_offset_changed(self) -> None:
        pass

    # ---------- max values ----------
    @Signal
    def max_throttle_changed(self) -> None:
        pass

    @Signal
    def max_brake_changed(self) -> None:
        pass

    @Signal
    def max_clutch_changed(self) -> None:
        pass

    @Signal
    def max_steering_changed(self) -> None:
        pass

    @Signal
    def all_speed_max_changed(self) -> None:
        pass

    # ---------- button status ----------
    @Signal
    def button_status_changed(self) -> None:
        pass

    @Signal
    def platform_status_changed(self) -> None:
        pass

    @Signal
    def pedal_status_changed(self) -> None:
        pass

    @Signal
    def head_tracking_status_changed(self) -> None:
        pass

    # ---------- head tracking ----------
    @Signal
    def head_tracking_yaw_angle_changed(self) -> None:
        pass

    # -------------------- properties --------------------
    # ---------- standard ----------
    throttle = Property(float, get_throttle, set_throttle, notify=throttle_changed)
    brake = Property(float, get_brake, set_brake, notify=brake_changed)
    clutch = Property(float, get_clutch, set_clutch, notify=clutch_changed)
    steering = Property(float, get_steering, set_steering, notify=steering_changed)

    steering_offset = Property(float, get_steering_offset, set_steering_offset, notify=steering_offset_changed)

    # ---------- actual values ----------
    actual_throttle = Property(float, get_actual_throttle, set_actual_throttle, notify=actual_throttle_changed)
    actual_brake = Property(float, get_actual_brake, set_actual_brake, notify=actual_brake_changed)
    actual_clutch = Property(float, get_actual_clutch, set_actual_clutch, notify=actual_clutch_changed)
    actual_steering = Property(float, get_actual_steering, set_actual_steering, notify=actual_steering_changed)

    # ---------- max values ----------
    max_throttle = Property(float, get_max_throttle, set_max_throttle, notify=max_throttle_changed)
    max_brake = Property(float, get_max_brake, set_max_brake, notify=max_brake_changed)
    max_clutch = Property(float, get_max_clutch, set_max_clutch, notify=max_clutch_changed)
    max_steering = Property(float, get_max_steering, set_max_steering, notify=max_steering_changed)
    all_speed_max = Property(float, get_all_speed_max, set_all_speed_max, notify=all_speed_max_changed)

    # ---------- button status ----------
    button_status = Property(bool, get_button_status, set_button_status, notify=button_status_changed)
    platform_status = Property(bool, get_platform_status, set_platform_status, notify=platform_status_changed)
    pedal_status = Property(bool, get_pedal_status, set_pedal_status, notify=pedal_status_changed)
    head_tracking_status = Property(bool, get_head_tracking_status, set_head_tracking_status, notify=head_tracking_status_changed)

    # ---------- head tracking ----------
    head_tracking_yaw_angle = Property(float, get_head_tracking_yaw_angle, set_head_tracking_yaw_angle, notify=head_tracking_yaw_angle_changed)
