from models.figures.Figure import Figure
from enums import FigureNames, Colors


class King(Figure):
    def __init__(self, cell, color: Colors):
        super().__init__(cell, color)
        self.name = FigureNames.KING
        self.is_first_step = True

    def can_move(self, target, attack=False, xray=False):
        if not super().can_move(target, attack=attack):
            return False

        direction = self.cell.x - target.x
        dx = abs(direction)
        dy = abs(self.cell.y - target.y)

        between_right = False
        rook_right = None
        if self.cell.x + 3 <= 7:
            for i in range(self.cell.x, self.cell.x + 4):
                if self.cell.board.get_cell(i, self.cell.y).is_under_attack:
                    between_right = True
                    break
            rook_right = self.cell.board.get_cell(self.cell.x + 3, self.cell.y).figure
            rook_right = rook_right and rook_right.name == FigureNames.ROOK
        rook_left = None
        between_left = False
        if self.cell.x - 4 <= 7:
            for i in range(self.cell.x, self.cell.x - 5, -1):
                if self.cell.board.get_cell(i, self.cell.y).is_under_attack:
                    between_left = True
                    break
            rook_left = self.cell.board.get_cell(self.cell.x - 4, self.cell.y).figure
            rook_left = rook_left and rook_left.name == FigureNames.ROOK

        return not target.is_under_attack \
            and ((dx <= 1 and dy <= 1) or
                 (self.is_first_step and dy == 0 and
                  ((direction == -2 and self.cell.is_empty_horizontal(target) and rook_right and not between_right)
                   or (direction == 2 and self.cell.is_empty_horizontal(target) and rook_left and not between_left))))

    def move_figure(self, target):
        self.is_first_step = False

        direction = self.cell.x - target.x
        dy = abs(self.cell.y - target.y)

        if dy == 0 and abs(direction) == 2:
            self.castled = True
