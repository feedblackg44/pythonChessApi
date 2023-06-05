from models.figures.Figure import Figure
from enums import FigureNames, Colors


class Bishop(Figure):
    def __init__(self, cell, color: Colors):
        super().__init__(cell, color)
        self.name = FigureNames.BISHOP

    def can_move(self, target, attack=False, xray=False):
        if not super().can_move(target, attack=attack):
            return False
        return self.cell.is_empty_diagonal(target, attack=attack, xray=xray)
