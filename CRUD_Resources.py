from pymongo import MongoClient
import os


class CRUD_Resources:

    def __init__(self):
        self.create_client()

    def create_client(self):
        conn_string = os.environ["DB"]
        client = MongoClient(conn_string)
        self.db = client.connect4

    def create_game(self, new_game):
        self.db.game_data.insert_one(new_game)

    def get_board(self, token):
        cur = self.db.game_data.find_one({"token": token})
        return cur["board"]

    def update_board(self, col, token):
        row = None
        cur = self.db.game_data.find_one({"token": token})
        if cur["status"] == "Progress":
            value = cur["turn"]
            query = {"token": token}
            last_board_status = cur["board"]
            for r in [5, 4, 3, 2, 1, 0]:
                if last_board_status[r][col] == 0:
                    last_board_status[r][col] = value
                    row = r
                    break
                elif r == 0:
                    return "Invalid Move! Try Choosing another column", None, None
            if value == 1:
                newvalues = {"$set": {"board": last_board_status, "turn": 2}}
                self.db.game_data.update_one(query, newvalues)
                stats = self.check_game_status(token, value)
                for i in last_board_status:
                    print("\n")
                    print(i)
                if stats:
                    query = {"token": token}
                    newvalues = {"$set": {"status": "Player 1 Wins"}}
                    self.db.game_data.update_one(query, newvalues)
                    return "Player 1 Wins", row, cur["p1Key"]
                return "Player 2 turn", row, cur["p1Key"]
            else:
                newvalues = {"$set": {"board": last_board_status, "turn": 1}}
                self.db.game_data.update_one(query, newvalues)
                stats = self.check_game_status(token, value)
                for i in last_board_status:
                    print("\n")
                    print(i)
                if stats:
                    query = {"token": token}
                    newvalues = {"$set": {"status": "Player 2 Wins"}}
                    self.db.game_data.update_one(query, newvalues)
                    return "Player 2 Wins", row, cur["p2Key"]
                return "Player 1 turn", row, cur["p2Key"]

        else:
            return cur["status"], None, None

    def check_game_status(self, token, value):
        cur = self.db.game_data.find_one({"token": token})
        board = cur["board"]

        # Check horizontally
        for c in range(7 - 3):
            for r in range(6):
                if board[r][c] == value and board[r][c + 1] == value and board[r][c + 2] == value and board[r][c + 3] == value:
                    return True

        # Check vertically
        for c in range(7):
            for r in range(6 - 3):
                if board[r][c] == value and board[r + 1][c] == value and board[r + 2][c] == value and board[r + 3][c] == value:
                    return True

        # Check diaganolly +
        for c in range(7 - 3):
            for r in range(6 - 3):
                if board[r][c] == value and board[r + 1][c + 1] == value and board[r + 2][c + 2] == value and board[r + 3][c + 3] == value:
                    return True

        # Check diagonally -
        for c in range(7 - 3):
            for r in range(3, 6):
                if board[r][c] == value and board[r - 1][c + 1] == value and board[r - 2][c + 2] == value and board[r - 3][c + 3] == value:
                    return True
        return False

    def update_users_data(self, row, col, player_id, token):
        self.db.users_moves_data.insert_one({"token": token, "col": col, "row": row, "player_id": player_id})

    def get_users_moves_data(self, token):
        data = []
        cur = self.db.users_moves_data.find({"token": token}, {'_id': False})
        for i in cur:
            data.append(i)
        return data

    def create_token(self, token):
        self.db.Tokens.insert_one({"token": token})


    def assert_token(self, token):
        cur = self.db.Tokens.find_one({"token": token})
        return cur
