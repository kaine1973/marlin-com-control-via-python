import re
import time

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

    def connect(self, port:str=None, baud_rate="250000"):
        if port is None:
            port = self.list_ports()[0].device
        self.__serial = Serial(port, baud_rate)
        # self.__serial.open()
        if self.__serial.isOpen():
            print("Connected!!")
            time.sleep(5)
            while True:
                resp = self.read_resp()
                print(resp)
                if resp == "":
                    break


    def send_code(self, command):
        self.__serial.write(bytes(command + "\n", "UTF-8"))
        print("SENT:", command)

        resp = self.read_resp()
        # print('\r',resp, end="")
        while "ok" not in resp:
            resp += self.read_resp()
            # print('\r',resp, end="")
            # self.send_code(command)
        return resp
    def read_resp(self):

        if self.__serial is not None and self.__serial.isOpen():
            return self.__serial.read_all().decode().strip()
        else:
            return None

    def stop(self):
        self.__stop = True

    def disconnect(self):
        if self.__serial is not None and self.__serial.isOpen():
            self.__serial.close()

    def __del__(self):
        self.disconnect()

# conn = Connector()

# conn.connect()
# while True:
#     print(conn.read_resp())
#     time.sleep(1)

def time_require():
    compiler = re.compile("[XYZ](\d+)")
    for distance in compiler.finditer("G0 X100 Y200"):
        print(distance.group(1))

time_require()