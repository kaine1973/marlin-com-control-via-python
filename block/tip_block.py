
from block import Block

tip_row = 1
tip_col = 12
tip_pos_lt = [174.20,213.70]
tip_pos_rb = [274.20,213.70]

class TipBlock(Block):

    def __init__(self, id):
        super().__init__(id)

    def prepare(self):
        pass


class FromBlock(Block):
    def __init__(self, id):
        super().__init__(id)

    # def next(self):
    #     new_col = self.priv_col + 1 if se
    #     return

class ToBlock(Block):
    def __init__(self, id):
        super().__init__(id)

    # def next(self):
    #     new_col = self.priv_col + 1 if se
    #     return



