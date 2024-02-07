from PySide6.QtCore import QObject, Signal, Property, Slot
import pynng

class NameModel(QObject):

    def __init__(self, pub_address, req_address) -> None:
        QObject.__init__(self)

        self.drivers = []

        self.pub_address = pub_address
        self.pub_socket = pynng.Pub0()
        self.pub_socket.listen(self.pub_address)

        self.req_sock = pynng.Req0()
        self.req_sock.dial(req_address, block=False)

    def send_data(self, driver_name):
        data = "current_driver: " + driver_name
        self.pub_socket.send(data.encode("utf-8"))

    @Slot(str)
    def name_changed(self, name: str):
        self.send_data(name)