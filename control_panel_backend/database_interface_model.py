from PySide6.QtCore import QObject, Signal, Slot, Property
import pynng
from time import sleep
import json


class DriverDataPublisher(QObject):
    driversChanged = Signal()
    statusChanged = Signal()

    def __init__(self, pub_address, req_address):
        QObject.__init__(self)
        self.__saved_drivers = []
        self.__drivers = [
            {
                "id": "4823662a-29c5-47d7-bdba-68baa2825990",
                "name": "Dummy",
                "email": "example@email.test",
                "created": "2023-11-02-08-58-03",
            }
        ]

        self.__status = ""

        self.PUB_ADDRESS = pub_address
        self.pub_socket = pynng.Pub0()
        self.pub_socket.listen(self.PUB_ADDRESS)
        sleep(1)

        self.req_socket = pynng.Req0()
        self.req_socket.dial(req_address, block=False)

    def sort_drivers(self, drivers):
        """
        Sorts a list of drivers based on their 'created' attribute.

        Args:
        drivers (list): The list of drivers to sort.

        Returns:
        list: The sorted list of drivers.
        """
        drivers.sort(key=lambda x: x["created"], reverse=True)
        return drivers

    @Slot(str)
    def send_data(self, driver_name):
        """
        Sends the current driver name to the publish socket.

        Args:
        driver_name (str): The name of the driver to send.
        """

        data = "current_driver: " + driver_name
        self.pub_socket.send(data.encode("utf-8"))
        self.status = f"Sent data: {driver_name}"

    @Slot()
    def refresh_driver(self):
        """Sends a request to refresh the driver data and handles the response."""

        data = "get_drivers"
        self.req_socket.send(data.encode("utf-8"))
        response = self.req_socket.recv().decode("utf-8")

        if response == "No Driver found":
            self.status = "No driver found"
        elif response == "Error":
            self.status = "Error while refreshing drivers"
        else:
            response = json.loads(response)
            response = self.sort_drivers(response)

            self.saved_drivers = response
            self.drivers = self.saved_drivers
            self.status = "Refreshed drivers"
        print(self.drivers)

    @Slot(str)
    def search_driver(self, name: str):
        """
        Searches for a driver by name.

        Args:
        name (str): The name of the driver to search for.
        """

        result = [driver for driver in self.drivers if driver["name"] == name]
        if result:
            self.drivers = result
            self.status = "Found driver " + name
        else:
            self.status = "No driver found"

    @Slot(str)
    def create_driver(self, name: str):
        """
        Creates a new driver with the given name.

        Args:
        name (str): The name of the driver to create.
        """

        data = f"post_driver: {name}"
        try:
            self.req_socket.send(data.encode("utf-8"))
            response = self.req_socket.recv().decode("utf-8")
            if response:
                try:
                    self.drivers.append(json.loads(response))
                    self.drivers = self.sort_drivers(self.drivers)
                    self.status = "Created driver: " + name
                except Exception as e:
                    print(e)
                    self.status = "Driver creation failed"
            else:
                self.status = "Driver creation failed"
        except:
            self.status = "Driver creation failed"

    @Property(list, notify=driversChanged)
    def drivers(self):
        return self.__drivers

    @Property(str, notify=statusChanged)
    def status(self):
        return self.__status

    @Property(list)
    def saved_drivers(self):
        return self.__saved_drivers

    @drivers.setter
    def drivers(self, value):
        if self.__drivers != value:
            self.__drivers = value
            self.driversChanged.emit()

    @status.setter
    def status(self, value):
        if self.__status != value:
            self.__status = value
            self.statusChanged.emit()

    @saved_drivers.setter
    def saved_drivers(self, value):
        if self.__saved_drivers != value:
            self.__saved_drivers = value
