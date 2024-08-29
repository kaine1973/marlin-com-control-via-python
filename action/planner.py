import re
import action
from block.block import Block, SourceBlock
from block.tip_block import TipBlock
from connection import Connector

current_X_Y_Z: list = [None, None, None]
z_home_pos = 270


class Tipper:
    def __init__(self, block: TipBlock):
        self.axis = "A"
        self.__tip_block = block
        self.__is_on = False
        self.__tip_height = 10   # cm
        self.__max_amount = 200  # ul
        self.__is_empty = False
        self.__left_amount = 0
    @property
    def tip_height(self):
        return self.__tip_height
    @property
    def max_amount(self):
        return self.__max_amount
    @property
    def is_on(self):
        return self.__is_on
    @property
    def is_empty(self):
        return self.__is_empty

    def empty(self):
        self.__left_amount = 0
        self.__is_empty = True
    def load(self):
        self.__is_on = True
    def unload(self):
        self.__is_on = False
        self.empty()
    def new_tip(self):
        if self.__is_on:
            self.unload()
        return self.__tip_block.get_next_valid_well()
    def tipper_block_z_height(self):
        return self.__tip_block.depth[0]

    @property
    def left_amount(self):
        return self.__left_amount
    @left_amount.setter
    def left_amount(self, left_amount: float):
        if left_amount < 0:
            raise RuntimeError("left_amount cannot be negative")
        self.__left_amount = left_amount

class Runner:
    def __init__(self, blocks: list[Block], tipper:Tipper, source_block:SourceBlock):
        self.conn = Connector()
        self.conn.connect()
        self.current_position = [None, None, None]
        self.blocks = blocks
        self.tipper = tipper
        self.source_block = source_block
        self.home_axis()

    def wait_for_pos(self, positions):
        while True:
            resp = self.conn.send_code("M114")
            resp = resp.strip()
            print(resp)
            match = re.match("X:([+\-\d]+)[.]\d{2} Y:([+\-\d]+)[.]\d{2} Z:([+\-\d]+)[.]\d{2} A:([+\-\d]+)[.]\d{2}",
                             resp)
            if match:
                reached = True
                matched = match.groups()
                for i in range(3):
                    if not str(positions[i]).startswith(matched[i]):
                        print(i, str(positions[i]), matched[i])
                        reached = False
                if reached:
                    break
    def safe_Z_position(self, position):
        safe_Z_position = current_X_Y_Z[2]
        if position[0] is not None:
            for block in self.blocks:
                if block.position_lt[1] <= current_X_Y_Z[1] <= block.position_rb[1]:
                    safe_Z_position = safe_Z_position if safe_Z_position > block.depth[1] else block.depth[1] + 5
        if position[1] is not None:
            for block in self.blocks:
                if block.position_lt[0] <= current_X_Y_Z[0] <= block.position_rb[0]:
                    safe_Z_position = safe_Z_position if safe_Z_position > block.depth[1] else block.depth[1] + 5

        safe_Z_position = safe_Z_position + (self.tipper.tip_height if self.tipper.is_on else 0)
        self.goto_position([None, None, safe_Z_position])

    def home_axis(self):
        for i in action.home():
            self.conn.send_code(i)
        self.wait_for_pos([0, 0, 0])
        self.current_position = [0, 0, z_home_pos]

    def goto_position(self, position: list, speed: float = 2500):
        if len(position) == 1:
            position = [position[0], None, None]
        elif len(position) == 2:
            position = [position[0], position[1], None]

        if position[0] is not None or position[1] is not None:
            self.safe_Z_position(position)

        self.conn.send_code("G0{}{}{} F{}\n".format(
            '' if position[0] is None else f' X{position[0]}',
            '' if position[1] is None else f' Y{position[1]}',
            '' if position[2] is None else f' Z{position[2]}',
            speed))
        self.wait_for_pos(position)
        self.current_position = [self.current_position[0] if position[0] is None else position[0],
                                 self.current_position[1] if position[1] is None else position[1],
                                 self.current_position[2] if position[2] is None else position[2]]
    def tipper_motion(self, amount, speed = 2200):
        self.conn.send_code("G0 A{} F{}\n".format(amount, speed))

    def mix(self, z_position: float):
        if z_position is not None:
            self.goto_position([None, None, z_position])
        for i in action.tip_mixing(0, 5, repeat=5):
            self.conn.send_code(i)

    def unload_tip(self, garbage_block:Block):
        self.to_block_top(garbage_block)
        self.tipper.unload()
        self.tipper.empty()

    def load_tip(self):
        if self.tipper.is_on:
            self.unload_tip()
        tip_well = self.tipper.new_tip()
        runner.goto_position(tip_well)
        runner.mix(self.tipper.tipper_block_z_height())

    def to_block_bottom(self, block:Block, target_col):
        if target_col is None:
            self.goto_position(block.get_current_valid_well())
        else:
            self.goto_position([block.get_current_valid_well()[0], target_col])
        self.goto_position([None,None,block.depth[0] + self.tipper.tip_height if self.tipper.is_on else 0])

    def to_block_top(self, block:Block):
        self.goto_position(block.get_current_valid_well())
        self.goto_position([None,None,block.depth[1] + self.tipper.tip_height if self.tipper.is_on else 0])

    def source_retract(self, source_block:SourceBlock):
        if source_block is None:
            source_block = self.source_block
        self.to_block_top(source_block)
        # 清空吸头
        if not self.tipper.is_empty:
            for command in action.home_axis(self.tipper.axis):
                self.conn.send_code(command)
            self.source_block.refill(self.tipper.left_amount)
            self.tipper.empty()
        self.tipper_motion(5)
        # 吸取容器剩余所有液体或者吸满吸头，取决于容器是否够当前吸头容量
        well_left = source_block.check_left_liquid()
        to_retract_amount = well_left if well_left < self.tipper.max_amount - 5 else self.tipper.max_amount - 5
        self.to_block_bottom(source_block)
        self.tipper_motion(to_retract_amount)
        self.source_block.well_retract(to_retract_amount)
        self.tipper.left_amount = to_retract_amount

    def extrude(self, amount:float, target_col, target_block:Block, source_block:SourceBlock):
        if source_block is None:
            source_block = self.source_block
        count = 0
        while self.tipper.left_amount < amount:
            self.source_retract(source_block)
            count += 1
            if count >= 3:
                raise RuntimeError('no more source liquid can be retracted')
        self.to_block_bottom(target_block, target_col)
        self.tipper_motion(-amount)


blocks = [Block(i+1) for i in range(4)]
tip = Tipper(TipBlock(1))
runner = Runner(blocks, tip)

