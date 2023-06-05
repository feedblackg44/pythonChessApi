from flask import Flask, request
from flask_cors import CORS
from models import Board

app = Flask(__name__)
CORS(app)

board = Board()


@app.route('/reset/<int:x>', methods=['GET'])
def reset_board(x):
    board.reset(int(x))
    return get_board()


@app.route('/get_board', methods=['GET'])
def get_board():

    board.reset_promotion()

    return board.to_json()


@app.route('/highlight_cells/<int:disable>', methods=['POST'])
def highlight(disable=0):
    if disable:
        board.reset_highlighting()
        return [False]

    cell1 = request.get_json()[0]
    cell = board.get_cell(cell1['x'], cell1['y'])
    board.highlight_cells(cell)

    return [True]


@app.route('/move_figure', methods=['POST'])
def move_piece():
    coords, coords_to = request.get_json()

    cell = board.get_cell(coords['x'], coords['y'])
    cell_to = board.get_cell(coords_to['x'], coords_to['y'])

    return [board.move_piece(cell, cell_to)]


@app.route('/can_move', methods=['POST'])
def can_move():
    coords, coords_to = request.get_json()

    return [board.can_move(coords, coords_to)]


@app.route('/promote', methods=['POST'])
def promote():
    new_name = request.get_json()

    return [board.promote(new_name[0])]


@app.route('/time_end', methods=['POST'])
def time_end():
    color = request.get_json()[0]

    return [board.check_end(color)]


if __name__ == '__main__':
    app.run(host='192.168.1.27',
            port=49048,
            debug=True)