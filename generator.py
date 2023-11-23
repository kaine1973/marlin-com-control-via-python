from connection import Connector
col = "ABCDEFGH"
codes = []


def generate():
    start_pos = "G0 X100 Y100 F7000"
    yield "G91"  # absolute
    yield start_pos
    yield "G91"  # relative
    for __col in range(12):
        __DIR = '' if __col % 2 == 1 else '-'
        for __row in range(8):
            yield "G0 E10 F1000"
            if __row < 7:
                yield f"G0 Y{__DIR}50 F4000"
        yield "G0 X50 7000"


conn = Connector()
conn.connect()
conn.stop()
# conn.list_ports()
conn.send_code("G91")
conn.send_code("G0 Y-400 F5000")
# conn.send_codes(generate())

