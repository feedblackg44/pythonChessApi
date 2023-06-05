from models.figures.Figure import Figure
from enums import FigureNames, Colors


class Rook(Figure):
    def __init__(self, cell, color: Colors):
        super().__init__(cell, color)
        self.name = FigureNames.ROOK
        self.is_first_step = True

    def can_move(self, target, attack=False, xray=False):
        if not super().can_move(target, attack=attack):
            return False

        if self.cell.is_empty_vertical(target, attack=attack, xray=xray):
            return True

        return self.cell.is_empty_horizontal(target, attack=attack, xray=xray)

    def move_figure(self, target):
        self.is_first_step = False
