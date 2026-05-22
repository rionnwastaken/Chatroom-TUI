from enum import IntEnum,auto,StrEnum


class Direction(IntEnum):
    FORWARD = auto()
    BACKWARD = auto()
    JUMP = auto()
    SCREEN_JUMP = auto()




class Status(IntEnum):
    OK = auto()
    ERR = auto()


class Padding():
    def __init__(self, top = 0, right = 0, bottom = 0, left = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_padding_horizontal_points(self):
        return self.right + self.left

    def get_padding_vertical_points(self):

        return self.top + self.bottom

class Push():
    def __init__(self, top = 0, right = 0, bottom = 0, left = 0):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def get_push_horizontal_points(self):
        return self.right + self.left

    def get_push_vertical_points(self):
        return self.bottom + self.top


class Where(StrEnum):
    CENTER_OF_SCREEN = auto()
