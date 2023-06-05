from enums import Colors, GameStates, FigureNames, SpecialMoves
from models.figures import Figure, Queen, Knight, Bishop, Rook
import uuid


class Cell:
    def __init__(self, board, x: int, y: int, color: Colors, figure=None):
        self.board = board
        self.x: int = x
        self.y: int = y
        self.color: Colors = color
        self.figure: Figure = figure
        self.available: bool = False
        self.on_way_check: bool = False
        self.on_way_block: dict[Colors: bool] = {Colors.WHITE: False, Colors.BLACK: False}
        self.attack_figures: list[Figure] = []

    @property
    def is_under_attack(self):
        return bool(len(self.attack_figures))

    def to_json(self):
        return {"x": self.x,
                "y": self.y,
                "color": self.color.value,
                "figure": self.figure.to_json() if self.figure else None,
                "available": self.available,
                "id": uuid.uuid4().hex}

    def is_empty(self, attack=False, xray=False):
        if attack and self.figure and self.figure.name == FigureNames.KING:
            return 1
        if xray and self.figure and self.figure.color == self.board.active_color:
            return 2
        return self.figure is None

    def is_enemy(self, target):
        if self.figure and target.figure:
            return self.figure.color != target.figure.color
        return False

    def is_empty_vertical(self, target, attack=False, xray=False):
        if self.x != target.x:
            return False
        min_y = min(self.y, target.y)
        max_y = max(self.y, target.y)
        flag = xray
        for y in range(min_y + 1, max_y):
            result = self.board.get_cell(self.x, y).is_empty(attack, xray)
            if result == 2:
                if flag:
                    flag = False
                else:
                    return False
            if not result:
                return False
        return True

    def is_empty_horizontal(self, target, attack=False, xray=False):
        if self.y != target.y:
            return False
        min_x = min(self.x, target.x)
        max_x = max(self.x, target.x)
        flag = xray
        for x in range(min_x + 1, max_x):
            result = self.board.get_cell(x, self.y).is_empty(attack, xray)
            if result == 2:
                if flag:
                    flag = False
                else:
                    return False
            if not result:
                return False
        return True

    def is_empty_diagonal(self, target, attack=False, xray=False):
        abs_x = abs(target.x - self.x)
        abs_y = abs(target.y - self.y)
        if abs_x != abs_y:
            return False

        dy = 1 if self.y < target.y else -1
        dx = 1 if self.x < target.x else -1

        flag = xray

        for i in range(1, abs_y):
            result = self.board.get_cell(self.x + dx * i, self.y + dy * i).is_empty(attack, xray)
            if result == 2:
                if flag:
                    flag = False
                else:
                    return False
            if not result:
                return False
        return True

    def set_figure(self, figure):
        self.figure = figure
        self.figure.cell = self

    def add_lost_figure(self, figure):
        if figure.color == Colors.BLACK:
            self.board.lost_black_figures.append(figure)
        else:
            self.board.lost_white_figures.append(figure)

    def can_move(self, target, attack=False, xray=False):
        color_block = Colors.BLACK
        if self.figure and self.figure.color == Colors.BLACK:
            color_block = Colors.WHITE
        if self.figure and \
                (attack or
                 ((not attack) and
                  self.figure.color == self.board.active_color)) and \
                (self.board.state == GameStates.NORMAL or
                 self.board.state == GameStates.PROMOTION or
                 (self.board.state == GameStates.CHECK and
                  ((len(self.board.king_attackers) < 2 and
                    target.on_way_check) or
                   self.figure.color != self.board.active_color or
                   self.figure.name == FigureNames.KING))) and \
                (not self.on_way_block[color_block] or
                 (self.on_way_block[color_block] and
                  target.on_way_block[color_block])) and \
                self.board.state != GameStates.MATE and \
                self.board.state != GameStates.TIE:
            return self.figure.can_move(target, attack, xray)
        else:
            return False

    def get_back_cell(self, target):
        direction = 1 if self.figure.color == Colors.BLACK else -1
        return self.board.get_cell(target.x, target.y + direction)

    def transform_figure(self, new_figure_name):
        if self.figure.name == FigureNames.PAWN:
            match new_figure_name:
                case FigureNames.QUEEN.value:
                    self.figure = Queen(self, self.figure.color)
                case FigureNames.ROOK.value:
                    self.figure = Rook(self, self.figure.color)
                case FigureNames.KNIGHT.value:
                    self.figure = Knight(self, self.figure.color)
                case FigureNames.BISHOP.value:
                    self.figure = Bishop(self, self.figure.color)
                case _:
                    return False
            return True
        return False

    def move_figure(self, target, name_transform=None):
        if self.figure and self.can_move(target):
            self.figure.move_figure(target)
            takes = False
            special = SpecialMoves.NORMAL
            figure = self.figure
            if target.figure:
                self.add_lost_figure(target.figure)
                takes = True
            elif self.figure.en_passant:
                self.figure.en_passant = False
                back_cell = self.get_back_cell(target)
                self.add_lost_figure(back_cell.figure)
                back_cell.figure = None
                takes = True
                special = SpecialMoves.EN_PASSANT
            if self.figure.castled:
                self.figure.castled = False
                rook_x = self.board.size - 1
                direction = -1
                special = SpecialMoves.SHORT_CASTLE
                if target.x < self.board.size / 2:
                    rook_x = 0
                    direction = 1
                    special = SpecialMoves.LONG_CASTLE
                rook = self.board.get_cell(rook_x, target.y)
                new_rook = self.board.get_cell(target.x + direction, target.y)
                new_rook.set_figure(rook.figure)
                rook.figure = None
            if self.figure.name == FigureNames.PAWN and (target.y == 7 or target.y == 0):
                if name_transform is None:
                    special = SpecialMoves.PROMOTE
                else:
                    self.transform_figure(name_transform)
            if special != SpecialMoves.PROMOTE:
                target.set_figure(self.figure)
                self.figure = None
            return [takes, special, figure]
        else:
            return []
