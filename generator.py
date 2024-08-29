from connection import Connector
from zone import Zone

col = "ABCDEFGH"


def generate():
    start_pos = "G0 X220 Y53 Z247 F3000"
    yield "G90"  # absolute
    yield start_pos
    yield "G91"  # relative
    for __col in range(12):
        __DIR = '' if __col % 2 == 1 else '-'
        for __row in range(8):
            yield "G0 E10 F1000"
            if __row < 7:
                yield f"G0 Y{__DIR}50 F3000"
        yield "G0 X50 F3000"



def test():
    release = [1200,0]
    liquid_tank = [223,70]
    height = 20
    liquid_left = 0
    liquid_each = 5
    liquid_full = 45
    liquid_tank_ccf = 16*4
    Z_start = 227
    tip_zone = Zone([257, 64], [351.7, 128], 20, 8, 12)
    yield "G28 Z"
    yield "G28"
    yield "G90"
    while True:
        valid_well = tip_zone.get_next_one_valid_well()
        if valid_well is None:
            yield f"G0 X{liquid_tank[0]} Y{liquid_tank[1]}"
            yield f"G0 Z{Z_start} F2000"
            yield f"G0 E{liquid_left} F200"
            liquid_left = 0
            break
        x, y = valid_well
        # 剩余液体不足，回液槽
        if liquid_left < liquid_each:
            yield f"G0 Z{Z_start}"
            yield f"G0 X{liquid_tank[0]} Y{liquid_tank[1]}"
            yield f"G0 Z{Z_start+height}"
            yield f"G0 E0 F450"
            yield f"G1 Z{Z_start+height+5} E-{liquid_full} F400"
            liquid_left = liquid_full
            yield f"G0 Z{Z_start} F3000"

        yield f"G0 Z{Z_start}"
        yield f"G0 X{x:.2f} Y{y:.2f}"

        liquid_left = liquid_left - liquid_each
        yield f"G91"
        yield f"G1 Z{5} E{liquid_each} F250"
        yield "G90"
        # yield f"G0 X{x-35} F5000"
        # yield f"G0 X{x} F5000"
        yield f"G0 Z{Z_start} F3000"



conn = Connector()
conn.connect(baud_rate=250000)

# conn.stop()
# # conn.list_ports()
# conn.send_code("G91")
# conn.send_code("G0 Y-400 F5000")
# conn.send_codes(generate())

codes = [x for x in test()]
conn.send_codes(codes)
# for x in test():
#     print(x)
conn.send_code("G28 Z X Y F3000")
