from models.figures.Figure import Figure
from enums import FigureNames, Colors


class Knight(Figure):
    def __init__(self, cell, color: Colors):
        super().__init__(cell, color)
        self.name = FigureNames.KNIGHT

    def can_move(self, target, attack=False, xray=False):
        if not super().can_move(target, attack=attack):
            return False

        dx = abs(self.cell.x - target.x)
        dy = abs(self.cell.y - target.y)

        return (dx == 1 and dy == 2) or (dx == 2 and dy == 1)
