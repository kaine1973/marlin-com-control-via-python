import numpy as np


class Zone:

    def __init__(self, start: [2], end: [2], height: int, row_count=8, col_count=12):
        self.__n_rows = row_count
        self.__n_cols = col_count
        self.__height = height
        self.__x_start, self.__y_start = start
        self.__x_end, self.__y_end = end

        self.__valid_col, self.__valid_row = 0, 0
        self.__container = None
        self.well_container()

    def well_container(self):
        self.__container = [[0] * self.__n_cols for _ in range(self.__n_rows)]
        x_gap = (self.__x_end - self.__x_start) / (self.__n_cols - 1)
        y_gap = (self.__y_end - self.__y_start) / (self.__n_rows - 1)
        for __i in range(self.__n_rows):
            for __j in range(self.__n_cols):
                self.__container[__i][__j] = [self.__x_start + (x_gap * __j), self.__y_start + (y_gap * __i)]

    def get_next_one_valid_well(self):
        valid = self.__container[self.__valid_row][self.__valid_col]

        self.__valid_row += 1
        if self.__valid_row == self.__n_rows:
            self.__valid_col += 1
            self.__valid_row = 0
        if self.__valid_col == self.__n_cols:
            return None
        return valid
