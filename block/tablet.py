import json
import os
from json import JSONDecodeError

tablets_save_path = "static/tablets"
if not os.path.exists(tablets_save_path):
    os.makedirs(tablets_save_path)

class Tablet(object):
    def __init__(self, __id=None):
        self.id = __id
        self.__save_path = f'{tablets_save_path}/{__id}.json'
        self.name = 'Tablet'
        self.__n_cols = 12
        self.__n_rows = 8
        self.__upper_margin = 8  # mm
        self.__left_margin = 8   # mm
        self.__depth = [0, 45]
        self.load_from_file(__id)

    def update_settings(self, name, nrows, ncols, depth_l, depth_h, um, lm):
        self.name = name
        self.__n_rows = nrows
        self.__n_cols = ncols
        self.__depth[1] = depth_h
        self.__depth[0] = depth_l
        self.__upper_margin = um
        self.__left_margin = lm

    def delete(self):
        if os.path.isfile(self.__save_path):
            os.remove(self.__save_path)

    @property
    def n_cols(self):
        return self.__n_cols

    @property
    def n_rows(self):
        return self.__n_rows
    @property
    def um(self):
        return self.__upper_margin
    @property
    def lm(self):
        return self.__left_margin
    @property
    def depth(self):
        return self.__depth

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

    def to_json(self):
        return json.dumps(self, default=lambda o: {k: v for k, v in o.__dict__.items()},
                          sort_keys=True, indent=4)

    def save_to_file(self):
        os.makedirs(os.path.dirname(os.path.abspath(tablets_save_path)), exist_ok=True)
        with open(f'{tablets_save_path}/{self.id}.json', "w") as file:
            file.write(self.to_json())


if __name__ == '__main__':
    if not os.path.isdir(tablets_save_path):
        os.mkdir(tablets_save_path)
    Tablet(1).save_to_file()
    Tablet(2).save_to_file()
    tablet_id = [x.split(".json")[0] for x in os.listdir(tablets_save_path)]
    print(tablet_id)

    tablets = {}
    for id in tablet_id:
        tablets[id] = Tablet(id)
        # tablets[id].name = f'Tablet{tablets[id].id}'
        print(tablets[id].name)
        # tablets[id].save_to_file()