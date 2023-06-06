from flask import Flask, request
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
    board.join_player(request.args.get('userId'), request.sid)
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    board.remove_player(request.sid)
    print('Client disconnected')


@socketio.on('board_update')
def handle_update_board():
    board.reset_promotion()
    black_sid = board.sids['black']
    if black_sid:
        board_data_black = board.to_json(black_sid)
        emit('board_update', board_data_black, room=black_sid)
        for sid in board.sids['Other']:
            board_data = board.to_json()
            emit('board_update', board_data, room=sid)
    else:
        board_data = board.to_json()
        emit('board_update', board_data, broadcast=True)


@app.route('/get_board/<string:uuid>', methods=['GET'])
def get_board(uuid):
    return board.to_json(uuid=uuid)


@app.route('/reset/<string:uuid>/<int:x>', methods=['GET'])
def reset_board(uuid, x):
    board.reset(uuid, int(x))
    return get_board(uuid)


@app.route('/highlight_cells/<string:uuid>/<int:disable>', methods=['POST'])
def highlight(uuid=None, disable=0):
    if disable:
        board.reset_highlighting()
        return [False]

    cell1 = request.get_json()[0]
    cell = board.get_cell(cell1['x'], cell1['y'])
    board.highlight_cells(cell, uuid)

    return [True]


@app.route('/move_figure/<string:uuid>', methods=['POST'])
def move_piece(uuid=None):
    coords, coords_to = request.get_json()

    cell = board.get_cell(coords['x'], coords['y'])
    cell_to = board.get_cell(coords_to['x'], coords_to['y'])

    return [board.move_piece(cell, cell_to, uuid)]


@app.route('/can_move/<string:uuid>', methods=['POST'])
def can_move(uuid=None):
    coords, coords_to = request.get_json()

    return [board.can_move(coords, coords_to, uuid)]


@app.route('/promote/<string:uuid>', methods=['POST'])
def promote(uuid=None):
    new_name = request.get_json()

    return [board.promote(uuid, new_name[0])]


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
        socketio.run(application,
                     **settings,
                     debug=True,
                     allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main(app)
