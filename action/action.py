from basic import uart_end,motion_axis


extruder_speed = 2300;
extruder_extrude_dir = "-";
extruder_retract_dir = "+";
extruder_air_amount = '10';
block_height = 30;

def home():
    yield f"M120{uart_end}"
    yield f"G91{uart_end}"
    yield f"G0 A40 F2000{uart_end}"
    yield f"G28 A{uart_end}"
    yield f"G28 Z{uart_end}"
    yield f"G28 X Y{uart_end}"
    yield f"M114{uart_end}"

def home_axis(axis):
    if axis == "X" or axis == "Y":
        home_axis("Z")
    yield f"G28 {axis}{uart_end}"
def finish_home():
    return ([x for x in home()] +
            [f"G90 {uart_end}",
            f"G0 Z-240 F2400{uart_end}"])


def go_to_rel(position:list[float], axis=None, feedrate=2200):

    if axis == None:
        axis = motion_axis
    if len(position) > 3:
        raise ValueError("go_to_rel: position can only have three values for XYZ axis")
        return
    axis_i = min(len(position), len(axis))
    if axis_i < 1:
        return

    motion = 'G0'
    for i in range(axis_i):
        if position[i] and axis[i] in motion_axis:
            motion += f' {axis[i]}{position[i]}'
    yield f"G90{uart_end}"
    yield f"{motion} F{feedrate}{uart_end}"

def extrude(amount, extruder_axis="A", feedrate = extruder_speed):
    yield f"G91{uart_end}"
    yield f"G0 {extruder_axis}{extruder_extrude_dir}{amount} F{feedrate}{uart_end}"

def retract(amount, extruder_axis="A", feedrate = extruder_speed):
    yield f"G91{uart_end}"
    yield f"G0 {extruder_axis}{extruder_retract_dir}{amount} F{feedrate}{uart_end}"
def retract_with_air(amount, extruder_axis="A", feedrate = extruder_speed):
    yield f"G91{uart_end}"
    yield f"G0 Z{block_height}{uart_end}"
    yield f"G28 A F1500{uart_end}"
    yield f"G0 A{extruder_air_amount}{uart_end}"
    yield f"G0 Z-{block_height}{uart_end}"
    yield f"G0 {extruder_axis}{extruder_retract_dir}{amount} F{feedrate}{uart_end}"

def extrude_with_up_down(ea, za, feedrate = extruder_speed):
    feedrate = min(feedrate, extruder_speed)
    yield f"G91"
    yield f"G1 Z{za} A{ea} F{feedrate}"


def tip_mixing(ea = 11, za = 11, repeat = 4, feedrate=extruder_speed):
    commands = []
    commands += home_axis("A") # or home
    commands += retract(abs(ea), 'A', feedrate=feedrate)

    for _ in range(repeat):
        commands += extrude_with_up_down(-ea, -za, feedrate)
        commands += extrude_with_up_down(ea, za, feedrate)
    return commands


if __name__ == "__main__":
    for i in tip_mixing(4):
        print(i)

