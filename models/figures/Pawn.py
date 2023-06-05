from models.figures.Figure import Figure
from enums import FigureNames, Colors


class Pawn(Figure):
    def __init__(self, cell, color: Colors):
        super().__init__(cell, color)
        self.name = FigureNames.PAWN
        self.is_first_step = True

    def can_move(self, target, attack=False, xray=False):
        if not super().can_move(target, attack=attack):
            return False

        direction = -1 if self.cell.figure.color == Colors.BLACK else 1
        first_step_direction = -2 if self.cell.figure.color == Colors.BLACK else 2

        if not attack and not self.cell.board.get_cell(self.cell.x, self.cell.y + direction).is_empty():
            first_step_direction += 1 if self.cell.figure.color == Colors.BLACK else -1

        if not attack and (target.y == self.cell.y + direction or (
                self.is_first_step and target.y == self.cell.y + first_step_direction)) \
                and target.x == self.cell.x \
                and self.cell.board.get_cell(target.x, target.y).is_empty():
            return True

        if abs(target.x - self.cell.x) == 1 and target.y == self.cell.y + direction:
            en_passant_cell = self.cell.board.get_cell(target.x, target.y - direction)
            if en_passant_cell.is_enemy(self.cell) and en_passant_cell.figure and \
                    en_passant_cell.figure.was_first_step:
                return True
            return self.cell.is_enemy(target) or attack
        return False

    def move_figure(self, target):
        if self.is_first_step:
            self.was_first_step = True
        else:
            self.was_first_step = False
        self.is_first_step = False

        if abs(self.cell.x - target.x) == 1 and abs(self.cell.y - target.y) == 1 and not target.figure:
            self.en_passant = True
