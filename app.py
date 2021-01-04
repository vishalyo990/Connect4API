from flask_restplus import Resource, Api
from flask import Flask, request
import jwt
import datetime
import uuid
from CRUD_Resources import CRUD_Resources
from functools import wraps
from flask_cors import CORS

row_count = 6
column_count = 7

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

app = Flask(__name__)
CORS(app)
api = Api(app, authorizations=authorizations, title='Connect 4 API')

app.config['SECRET_KEY'] = 'secretKey'

moves_parser = api.parser()
moves_parser.add_argument('col', type=int, help='Columns number of the move (0-6)', location='form')


# Checking Tokens
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        crud = CRUD_Resources()
        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']
        if not token:
            return {'message': 'Token is missing!'}
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            cur = crud.assert_token(token)
            if not cur:
                return {'message': 'Token is invalid!'}
        except Exception as e:
            return {'message': 'Token is invalid!: '+str(e)}
        return f(token, *args, **kwargs)
    return decorated


# To Create a new Game
@api.route("/start")
class GameResources(Resource):
    @staticmethod
    def get():
        crud = CRUD_Resources()
        token = jwt.encode(
            {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=4800)},
            app.config['SECRET_KEY'])
        crud.create_token(token.decode())
        new_game = {
            "p1Key": uuid.uuid4().hex,
            "p2Key": uuid.uuid4().hex,
            "board": [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]],
            "boardId": uuid.uuid4().hex,
            "turn": 1,
            "status": "Progress",
            "token": token.decode()
        }
        crud.create_game(new_game)
        return {"message": "Ready, Use Token: " + str(token.decode())}


@api.route("/play")
class PlayResources(Resource):

    # To play the game
    @staticmethod
    @token_required
    @api.doc(security='apikey')
    @api.expect(moves_parser)
    def put(token):
        crud = CRUD_Resources()
        data = request.form
        col = int(data["col"])
        print(col)
        if col > 6 or col < 0:
            print(col)
            return {"message": "Invalid Inputs (Column must be in range of (0 - 6))"}
        message, row, player_id = crud.update_board(col, token)
        if row is None:
            return {"message": message}
        crud.update_users_data(row, col, player_id, token)
        return {"message: ": message}


@api.route("/moves")
class MovesResources(Resource):
    # To fetch all moves associated to the respective game (Only needs Token to determine the game)
    @staticmethod
    @token_required
    @api.doc(security='apikey')
    def get(token):
        crud = CRUD_Resources()
        cur_data = crud.get_users_moves_data(token)
        return {"data": cur_data}


@api.route("/board")
class BoardResources(Resource):
    # To fetch the status of the board
    @staticmethod
    @token_required
    @api.doc(security='apikey')
    def get(token):
        crud = CRUD_Resources()
        cur_data = crud.get_board(token)
        print(cur_data)
        return {"data": cur_data}


if __name__ == "__main__":

    app.run("0.0.0.0", port=5025)