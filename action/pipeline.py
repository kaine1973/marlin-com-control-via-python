import re
import time

from block.block import Block
import action

from connection import Connector

conn = Connector()
conn.connect()


def runner(steps):
    for step in steps:
        conn.send_code(step)


def wait_for_pos(positions):
    while True:
        resp = conn.send_code("M114")
        resp = resp.strip()
        print(resp)
        match = re.match("X:([+\-\d]+)[.]\d{2} Y:([+\-\d]+)[.]\d{2} Z:([+\-\d]+)[.]\d{2} A:([+\-\d]+)[.]\d{2}", resp)
        if match:
            reached = True
            matched = match.groups()
            for i in range(3):
                if not str(positions[i]).startswith(matched[i]):
                    print(i, str(positions[i]), matched[i])
                    reached = False
            if reached:
                break


def pipeline():
    tipper = Block(1)
    ci_zhu = Block(4)
    tablets = [Block(i) for i in [7, 5, 8]]
    ## home
    runner(action.home())
    #
    # tipper.get_next_one_valid_well()
    valid_tip = tipper.get_next_valid_well()
    runner(action.go_to_rel(valid_tip, feedrate=3200))

    Z_min = -240
    # tipper
    runner(action.home_axis("Z"))
    runner(action.go_to_rel([None, None, tipper.depth[1] + Z_min], feedrate=3000))

    mix_range = tipper.depth[0] - tipper.depth[1]
    runner(action.tip_mixing(0, mix_range, 3))
    Z_min = -240 + 80
    runner(action.go_to_rel([None, None, tipper.depth[1] + Z_min], feedrate=3000))
    wait_for_pos(valid_tip + [tipper.depth[1] + Z_min])

    ci_zhu_well = ci_zhu.get_next_valid_well()
    full_amount = 180
    amount_per_well = 30
    left_amount = 0
    current_block = Block(7)

    while True:
        current_block_current_well = current_block.get_next_valid_well()
        if current_block_current_well is None:
            break

        if left_amount < amount_per_well:
            runner(action.go_to_rel(ci_zhu_well, feedrate=3000))
            runner(action.go_to_rel([None, None, ci_zhu.depth[1] + 10 + -240], feedrate=3000))
            runner(action.go_to_rel(ci_zhu_well, feedrate=3000))
            runner(action.go_to_rel([None, None, ci_zhu.depth[0] + -240], feedrate=3000))
            runner(action.tip_mixing(20, 0, 5))
            runner(action.home_axis("A"))
            runner(action.retract(amount=full_amount))
            left_amount = full_amount
            runner(action.go_to_rel([None, None, ci_zhu.depth[1] + -240], feedrate=3000))

        runner(action.go_to_rel([None, None, current_block.depth[1] + 10 + -240], feedrate=3000))
        runner(action.go_to_rel(current_block_current_well, feedrate=3000))
        runner(action.go_to_rel([None, None, current_block.depth[1] + -240], feedrate=3000))
        runner(action.extrude(amount=amount_per_well, feedrate=2300))
        left_amount = left_amount - amount_per_well

    # 排液
    if left_amount > 0:
        runner(action.go_to_rel([None, None, ci_zhu.depth[1] + 10 + -240], feedrate=3000))
        runner(action.go_to_rel(ci_zhu_well, feedrate=3000))
        runner(action.go_to_rel([None, None, ci_zhu.depth[0] + -240], feedrate=3000))
        runner(action.extrude(left_amount))

    # untipper
    runner(action.go_to_rel([None, None, tipper.depth[1] + Z_min], feedrate=3000))
    runner(action.go_to_rel(valid_tip, feedrate=3200))
    Z_min = -240
    runner(action.go_to_rel([None, None, tipper.depth[1] + Z_min + 20], feedrate=3000))
    runner(action.home_axis('A'))
    runner(action.retract(10))
    runner(['M121'])
    runner(action.extrude(40))
    runner(action.retract(50))
    runner(action.home_axis('A'))

    time.sleep(10)


if __name__ == "__main__":
    # wait_for_pos([0,271.11,0,0])
    pipeline()
