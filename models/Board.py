import time

from models.figures import Figure, King, Knight, Pawn, Queen, Bishop, Rook
from models.History import History
from models.Cell import Cell
from enums import GameStates, Colors, FigureNames, SpecialMoves


class Board:
    def __init__(self):
        self.size = 8
        self.cells: list[list[Cell]] = []
        self.lost_black_figures: list[Figure] = []
        self.lost_white_figures: list[Figure] = []
        self.history: History = History()
        self.state: GameStates = GameStates.NORMAL
        self.active_color: Colors = Colors.WHITE
        self.won: Colors | None = None
        self.times: list[int] = []
        self.time_start: int = 0
        self.first: bool = True
        self.cells_to_promote: list[Cell | None] = []
        self.saved_state: GameStates | None = None
        self.king_attackers: list[Figure] = []

        self.reset(600)

    # ---- Interaction ---- #

    def get_cell(self, x, y) -> Cell:
        return self.cells[y][x]

    def can_move(self, coords, coords_to):
        if self.state != GameStates.MATE and self.state != GameStates.TIE:
            cell = self.get_cell(coords['x'], coords['y'])
            cell_to = self.get_cell(coords_to['x'], coords_to['y'])

            if cell.can_move(cell_to):
                return True
            self.highlight_cells(cell, disable=True)
            return False
        else:
            print("END!")
            return False

    def update_time(self):
        if not self.first and self.state != GameStates.TIE and self.state != GameStates.MATE:
            index = 0 if self.active_color == Colors.WHITE else 1
            self.times[index] -= int(time.time()) - self.time_start
        self.time_start = int(time.time())

    def switch_turn(self):
        if self.active_color == Colors.WHITE:
            self.active_color = Colors.BLACK
        else:
            self.active_color = Colors.WHITE
        self.make_board_attacks()
        if self.first:
            self.first = False
        self.update_time()

    def empty_attackers(self):
        for row in self.cells:
            for cell in row:
                cell.attack_figures = []
                cell.on_way_check = False
                cell.on_way_block = {Colors.WHITE: False, Colors.BLACK: False}
                if cell.figure:
                    cell.figure.is_checking = False
        self.king_attackers = []

    def make_cells_on_way_check(self, cell, cell2, xray=False):
        color = cell.figure.color
        cell.figure.is_checking = True
        if cell.x == cell2.x and cell.y != cell2.y:
            step = -1
            if cell.y < cell2.y:
                step = 1
            for i in range(cell.y, cell2.y, step):
                cell_ = self.get_cell(cell.x, i)
                if xray:
                    cell_.on_way_block[color] = True
                else:
                    cell_.on_way_check = True
        elif cell.x != cell2.x and cell.y == cell2.y:
            step = -1
            if cell.x < cell2.x:
                step = 1
            for i in range(cell.x, cell2.x, step):
                cell_ = self.get_cell(i, cell.y)
                if xray:
                    cell_.on_way_block[color] = True
                else:
                    cell_.on_way_check = True
        elif abs(cell.x - cell2.x) == abs(cell.y - cell2.y):
            step_x = -1
            if cell.x < cell2.x:
                step_x = 1
            step_y = -1
            if cell.y < cell2.y:
                step_y = 1
            i = cell.x
            j = cell.y
            while i != cell2.x or j != cell2.y:
                cell_ = self.get_cell(i, j)
                if xray:
                    cell_.on_way_block[color] = True
                else:
                    cell_.on_way_check = True
                i += step_x
                j += step_y

    def make_board_attacks(self):
        self.empty_attackers()
        flag_checked = False
        for row in self.cells:
            for cell2 in row:
                if cell2.figure and cell2.figure.was_first_step:
                    if cell2.figure.color == self.active_color:
                        cell2.figure.was_first_step = False
                for row2 in self.cells:
                    for cell in row2:
                        if cell.figure and cell.figure.color != self.active_color:
                            if cell.can_move(cell2, attack=True):
                                if cell2.figure and cell2.figure.color == self.active_color \
                                        and cell2.figure.name == FigureNames.KING:
                                    self.state = GameStates.CHECK
                                    flag_checked = True
                                    self.make_cells_on_way_check(cell, cell2)
                                    self.king_attackers.append(cell.figure)
                                cell2.attack_figures.append(cell.figure)
                            if cell.can_move(cell2, attack=True, xray=True):
                                if cell2.figure and cell2.figure.color == self.active_color \
                                        and cell2.figure.name == FigureNames.KING:
                                    self.make_cells_on_way_check(cell, cell2, xray=True)

        if not flag_checked:
            self.state = GameStates.NORMAL
        self.check_if_any_can_move()

    def check_if_any_can_move(self):
        only_kings = True
        any_can_move = False
        for row in self.cells:
            for cell in row:
                if cell.figure and cell.figure.name != FigureNames.KING:
                    only_kings = False
                if cell.figure and cell.figure.color == self.active_color:
                    for row2 in self.cells:
                        for cell2 in row2:
                            if cell.can_move(cell2):
                                any_can_move = True
        if not any_can_move:
            if self.state == GameStates.CHECK:
                self.state = GameStates.MATE
                color = Colors.BLACK if self.active_color == Colors.WHITE else Colors.WHITE
                self.won = color
                self.active_color = None
                return False
        if only_kings:
            self.state = GameStates.TIE
            self.active_color = None
            return False
        return True

    def check_end(self, color):
        if self.active_color is None:
            return False
        index = 0 if color == Colors.WHITE.value else 1
        color_won = Colors.WHITE if color == Colors.BLACK.value else Colors.BLACK
        if self.times[index] - (int(time.time()) - self.time_start) <= 0:
            self.times[index] = 0
            self.state = GameStates.MATE
            self.active_color = None
            self.won = color_won
            return True
        else:
            return False

    def reset_highlighting(self):
        for row in self.cells:
            for target in row:
                target.available = False

    def highlight_cells(self, selected_cell: Cell, disable=False):
        for row in self.cells:
            for target in row:
                target.available = bool(selected_cell.figure and selected_cell.can_move(target) and not disable)

    def promote(self, transform):
        result = self.move_piece(*self.cells_to_promote, transform)
        self.reset_promotion()
        return result

    def reset_promotion(self):
        if self.state == GameStates.PROMOTION:
            self.cells_to_promote = [None, None]
            self.state = self.saved_state
            self.saved_state = None

    def move_piece(self, cell, cell_to, transform=None):
        if self.state != GameStates.MATE and self.state != GameStates.TIE:
            self.highlight_cells(cell, disable=True)
            result = cell.move_figure(cell_to, transform)
            if len(result):
                if result[1] == SpecialMoves.PROMOTE:
                    self.saved_state = self.state
                    self.state = GameStates.PROMOTION
                    self.cells_to_promote = [cell, cell_to]
                    return -1
                else:
                    self.switch_turn()
                    turn = {"figure": result[2],
                            "cell_from": cell,
                            "turn_type": result[0],
                            "cell_to": cell_to,
                            "special": result[1],
                            "state": self.state,
                            "won": self.won}
                    self.history.add_turn(**turn)
                    return 1
        return 0

    # ---- Initialization ---- #

    def reset(self, time_init):
        self.size = 8
        self.cells: list[list[Cell]] = [[Cell(self, j, i, Colors.WHITE if (i + j) % 2 else Colors.BLACK)
                                        for j in range(self.size)] for i in range(self.size)]
        self.lost_black_figures: list[Figure] = []
        self.lost_white_figures: list[Figure] = []
        self.history: History = History()
        self.state: GameStates = GameStates.NORMAL
        self.active_color: Colors = Colors.WHITE
        self.won: Colors | None = None
        self.times: list[int] = [time_init, time_init]
        self.time_start = 0
        self.first = True
        self.cells_to_promote: list[Cell | None] = [None, None]
        self.saved_state: GameStates | None = None
        self.king_attackers: list[Figure] = []

        self.set_figures()

    def set_figures(self):
        self.add_bishops()
        self.add_kings()
        self.add_knights()
        self.add_pawns()
        self.add_queens()
        self.add_rooks()

    def add_bishops(self):
        Bishop(self.get_cell(2, 0), Colors.WHITE)
        Bishop(self.get_cell(5, 0), Colors.WHITE)
        Bishop(self.get_cell(2, 7), Colors.BLACK)
        Bishop(self.get_cell(5, 7), Colors.BLACK)

    def add_kings(self):
        King(self.get_cell(4, 0), Colors.WHITE)
        King(self.get_cell(4, 7), Colors.BLACK)

    def add_knights(self):
        Knight(self.get_cell(1, 0), Colors.WHITE)
        Knight(self.get_cell(6, 0), Colors.WHITE)
        Knight(self.get_cell(1, 7), Colors.BLACK)
        Knight(self.get_cell(6, 7), Colors.BLACK)

    def add_pawns(self):
        for i in range(self.size):
            Pawn(self.get_cell(i, 1), Colors.WHITE)
            Pawn(self.get_cell(i, 6), Colors.BLACK)

    def add_queens(self):
        Queen(self.get_cell(3, 0), Colors.WHITE)
        Queen(self.get_cell(3, 7), Colors.BLACK)

    def add_rooks(self):
        Rook(self.get_cell(0, 0), Colors.WHITE)
        Rook(self.get_cell(7, 0), Colors.WHITE)
        Rook(self.get_cell(0, 7), Colors.BLACK)
        Rook(self.get_cell(7, 7), Colors.BLACK)

    # ---- Printing ---- #

    def to_json(self) -> dict:
        self.update_time()
        cells = [[self.get_cell(i, j).to_json()]
                 for j in range(self.size - 1, -1, -1)
                 for i in range(self.size)]
        return {"cells": cells,
                "lost_white": [figure.to_json() for figure in self.lost_white_figures],
                "lost_black": [figure.to_json() for figure in self.lost_black_figures],
                "history": self.history.to_json(),
                "active": self.active_color.value if self.active_color else None,
                "state": self.state.value,
                "time": self.times,
                "first": self.first,
                "won": self.won.value if self.won else None}
