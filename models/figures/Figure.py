from enums import Colors, FigureNames
import uuid


class Figure:
    def __init__(self, cell, color: Colors):
        self.color = color
        self.cell = cell
        self.cell.figure = self
        self.name = FigureNames.FIGURE
        self.is_first_step = False
        self.was_first_step = False
        self.castled = False
        self.en_passant = False

    def to_json(self):
        return {"color": self.color.value,
                "name": self.name.value,
                "id": uuid.uuid4().hex}

    def can_move(self, target, attack=False, xray=False):
        if not attack and target.figure and \
                (target.figure.color == self.color or target.figure.name == FigureNames.KING):
            return False
        elif self.cell.x == target.x and self.cell.y == target.y:
            return False
        return True

    def move_figure(self, target):
        pass
