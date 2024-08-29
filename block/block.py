import json
import os.path
from json import JSONDecodeError

from .tablet import Tablet
from error import SourceRunout


layouts_save_path = "static/layouts"
blocks_save_path = "static/blocks"
class Block(object):
    def __init__(self, id):
        self.__save_path = f"{blocks_save_path}/block_{id}.json"
        self.__block_number = id
        self.__block_name = f"Block_{self.__block_number}"
        self.__position_lt = [0, 0]
        self.__position_rb = [0, 0]
        self.__tablet = None

        self.__y_gap = 0
        self.__x_gap = 0

        self.load_from_file()

        self.__valid_col, self.__valid_row = 0, 0
        if self.__tablet is not None:
            self.__init_wells()

    def apply_tablet(self, id):
        self.__tablet = Tablet(id)
        self.__init_wells()

    def __init_wells(self):
        if self.__tablet is None:
            return
        self.__wells = [[0] * self.col_count for _ in range(self.row_count)]
        self.__x_gap = 0 if self.col_count == 1 else (self.__position_rb[0] - self.__position_lt[0] - self.__tablet.lm) / (
                self.col_count - 1)
        self.__y_gap = 0 if self.row_count == 1 else (self.__position_rb[1] - self.__position_lt[1] - self.__tablet.um) / (
                self.row_count - 1)
        for __i in range(self.row_count):
            for __j in range(self.col_count):
                self.__wells[__i][__j] = [self.__position_lt[0] + self.__tablet.lm + (self.__x_gap * __j),
                                          self.__position_lt[1] + self.__tablet.um + (self.__y_gap * __i)]

        self.save_to_file()

    def get_next_valid_well(self) -> (int, int):
        # if self.__valid_row is None or self.__valid_col is None:
        #     return None
        # prev_valid = self.__wells[self.__valid_row][self.__valid_col]

        if self.__valid_row + 1 == self.row_count:
            if self.__valid_col + 1 == self.col_count:
                self.__valid_row = None
                self.__valid_col = None
            else:
                self.__valid_col += 1
                self.__valid_row = 0
        else:
            self.__valid_row += 1
        if self.__valid_row is None or self.__valid_col is None:
            return None
        return self.__wells[self.__valid_row][self.__valid_col]

    def get_current_valid_well(self):
        if self.__valid_row is not None and self.__valid_col is not None:
            return self.__wells[self.__valid_row][self.__valid_col]
        else:
            return self.get_next_valid_well()

    def to_json(self):
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items()},
                          sort_keys=True, indent=4)

    @property
    def y_gap(self):
        return self.__y_gap

    @property
    def x_gap(self):
        return self.__x_gap

    @property
    def depth(self):
        return self.__tablet.depth

    @property
    def block_number(self):
        return self.__block_number

    @property
    def block_name(self):
        return self.__block_name

    @block_name.setter
    def block_name(self, name):
        self.__block_name = name

    @property
    def position_lt(self):
        return self.__position_lt

    @position_lt.setter
    def position_lt(self, x: list[int]) -> None:
        if x[0] > self.__position_rb[0] or x[1] > self.__position_rb[1]:
            raise ValueError("Position left top must be smaller than position right bottom.")
        self.__position_lt = [x[0], x[1]]
        self.__init_wells()

    @property
    def position_rb(self):
        return self.__position_rb

    @position_rb.setter
    def position_rb(self, x: list[int]) -> None:
        if x[0] < self.__position_lt[0] or x[1] < self.__position_lt[1]:
            raise ValueError("Position rb must be greater than position left top.")
        self.__position_rb = [x[0], x[1]]
        self.__init_wells()

    @property
    def row_count(self):
        return self.__tablet.n_rows
    @property
    def valid_col(self):
        return self.__valid_col

    @row_count.setter
    def row_count(self, x: int) -> None:
        if x < 1:
            raise ValueError("Row count must be greater than or equal to 1")
        self.__row_count = x
        self.__init_wells()

    @property
    def col_count(self):
        return self.__col_count

    @col_count.setter
    def col_count(self, x: int) -> None:
        if x < 1:
            raise ValueError("Column count must be greater than or equal to 1")
        self.__col_count = x
        self.__init_wells()

    def save_to_file(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.__save_path)), exist_ok=True)
        with open(self.__save_path, "w") as file:
            file.write(self.to_json())

    def load_from_file(self) -> bool:
        if not os.path.isfile(self.__save_path):
            return False
        with open(self.__save_path, "r") as file:
            try:
                data = json.loads(''.join(file.readlines()))
                for k, v in data.items():
                    self.__dict__[k] = v
            except JSONDecodeError:
                return False

        return True

# class Block_Type:
#
class SourceBlock(Block):
    def __init__(self, id):
        super().__init__(id)
        self.__well_contain_amount = 5000
        self.__well_left_amount:{int:float} = {}
        self.init_well_amount()

    def init_well_amount(self):
        self.__well_left_amount = { x: self.__well_contain_amount for x in range(self.col_count) }

    def check_left_liquid(self):
        return self.__well_left_amount[self.valid_col]

    def well_retract(self, amount):
        if self.__well_left_amount[self.valid_col] <= amount:
            self.__well_left_amount[self.valid_col] = 0
            # self.get_next_valid_well()
        else:
            self.__well_left_amount[self.valid_col] -= amount

    def refill(self, amount):
        self.__well_left_amount[self.valid_col] += amount

    def get_next_valid_well(self):
        print("source_block,get_next_valid_well")
        if self.check_left_liquid() <= 0:
            next_well = super().get_next_valid_well()
            if next_well is None:
                raise SourceRunout
            else:
                return next_well
        else:
            return self.get_current_valid_well()

class Layout:
    def __init__(self, id = None):
        self.id = id
        self.__save_path = f'{layouts_save_path}/{self.id}.json'
        self.name = '布局'
        self.config = {}
        self.load_from_file(id)

    def add_config(self, key, value):
        self.config[key] = value

    def to_json(self):
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items()},
                          sort_keys=True, indent=4)


    def save_to_file(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.__save_path)), exist_ok=True)
        with open(self.__save_path, "w") as file:
            file.write(self.to_json())

    def load_from_file(self, id):
        if not os.path.isfile(self.__save_path):
            return False
        with open(self.__save_path, "r") as file:
            try:
                data = json.loads(''.join(file.readlines()))
                for k, v in data.items():
                    self.__dict__[k] = v
            except JSONDecodeError:
                return False

        return True

if __name__ == "__main__":
    source_block = SourceBlock(4)
    block = Block(7)
    block.apply_tablet(1)
    source_well = None
    block_well = None
    try:
        source_well = source_block.get_next_valid_well()
        print(source_well)
        source_block.well_retract(5000)
        source_well = source_block.get_next_valid_well()
        print(source_well)
        source_well = source_block.get_next_valid_well()
        source_well = source_block.get_next_valid_well()
    except SourceRunout:
        input('please refill:')
    block_well = block.get_next_valid_well()
    print(source_well)
    print(block_well)
