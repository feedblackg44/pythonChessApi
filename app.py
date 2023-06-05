from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from models import Board
from json import load, dumps
from os.path import isfile

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

board = Board()


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('board_update')
def handle_update_board():
    update_board_data()


def update_board_data():
    board.reset_promotion()
    board_data = board.to_json()
    emit('board_update', board_data, broadcast=True)


@app.route('/get_board', methods=['GET'])
def get_board():
    socketio.emit('update_board')
    return board.to_json()


@app.route('/reset/<int:x>', methods=['GET'])
def reset_board(x):
    board.reset(int(x))
    return get_board()


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


def main(application):
    # Default Data
    default_settings = {
        "host": "localhost",
        "port": 5000
    }
    filename = "web_settings.json"
    json_object = dumps(default_settings, indent=4)
    if not isfile(filename):
        with open(filename, "w") as file:
            file.write(json_object)

    # Load settings and run app
    with open(filename, "r") as file:
        settings = load(file)
        socketio.run(app,
                     **settings,
                     debug=True,
                     allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main(app)
