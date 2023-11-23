from serial import Serial
from serial.tools import list_ports


class Connector:

    __serial = None
    __stop = False

    def __init__(self):
        # self._serial: serial.Serial
        pass

    def list_ports(self):
        __ports = list_ports.grep("usb")
        __port_links = []
        print("----------------")
        print("Available ports:")
        for _port in __ports:
            print(">", _port.device)
            __port_links.append(_port)
        print("----------------")
        return __port_links

    def connect(self, port=None, baud_rate="115200"):
        if port is None:
            port = self.list_ports()[0].device
        self.__serial = Serial(port, baud_rate)
        # self.__serial.open()
        if self.__serial.isOpen():
            while self.read_resp() is None:
                print("Connected!!")
        print(self.__serial.readline())

    def send_code(self, command):
        self.__serial.write(bytes(command + "\n", "UTF-8"))
        print("SENT:", command)
        while True:
            resp = self.read_resp()
            print("++", resp, "++")
            if resp == "ok":
                return

    def send_codes(self, commands):
        for command in commands:
            if self.__stop:
                break
            self.send_code(command)

    def read_resp(self):
        if self.__serial is not None and self.__serial.isOpen():
            return self.__serial.readline().decode().strip()
        else:
            return None

    @property
    def stop(self):
        return self.__stop

    @stop.setter
    def stop(self, value):
        self.__stop = True

    def disconnect(self):
        if self.__serial is not None and self.__serial.isOpen():
            self.__serial.close()

    def __del__(self):
        self.disconnect()
