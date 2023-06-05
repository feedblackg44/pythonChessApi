from enums import SpecialMoves, GameStates


class History:
    def __init__(self):
        self.history = [[]]

    def to_json(self):
        return self.history

    def add_turn(self, figure, cell_from, turn_type, cell_to,
                 special=SpecialMoves.NORMAL,
                 state=GameStates.NORMAL,
                 won=None):
        turn = {"figure": figure.to_json(),
                "from": [cell_from.x, cell_from.y],
                "take": turn_type,
                "to": [cell_to.x, cell_to.y],
                "special": special.value,
                "state": state.value,
                "won": won.value if won else None}
        if len(self.history[-1]) > 1:
            self.history.append([])
        self.history[-1].append(turn)

    def get_last_turn(self):
        return self.history[-1][-1]
