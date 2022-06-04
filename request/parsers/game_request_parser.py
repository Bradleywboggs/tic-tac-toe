from typing import Optional

from data_source.data_source import DataSource
from gamestate.data import Player, GameId, Move, GameState, XO, XCoord, YCoord
from request.data import PlayerUpdate, MoveUpdate, GameStateError

ID_KEY = "id"
TYPE_KEY = "type"
DATA_KEY = "data"
ATTRIBUTES_KEY = "attributes"
RELATIONSHIPS_KEY = "relationships"

GAMES_TYPE = "games"


def validate_existing_game(
    request_data: dict, path_game_id: GameId, data_source: DataSource
) -> GameStateError | GameState:
    if not request_data.get(DATA_KEY, {}) or not isinstance(
        request_data[DATA_KEY], dict
    ):
        return GameStateError.InvalidRequestBody

    if request_data[DATA_KEY].get(TYPE_KEY) != GAMES_TYPE:
        return GameStateError.WrongResourceType

    if request_data[DATA_KEY].get(ID_KEY) != path_game_id:
        return GameStateError.GameIdConflict

    existing_game_state: Optional[GameState] = data_source.get_game(path_game_id)

    if not existing_game_state:
        return GameStateError.GameNotFound

    if existing_game_state.game_is_over:
        return GameStateError.GameIsOver

    return existing_game_state


def parse_player_from_game_create_request(
    user_id: str | None, data_source: DataSource
) -> GameStateError | Player:
    if user_id is None:
        return GameStateError.MissingUserIdHeader

    existing_player = data_source.get_player(user_id)
    if existing_player is None:
        return GameStateError.PlayerDoesNotExist
    return existing_player


def parse_update_request(
    request_data: dict, existing_game_state: GameState, data_source: DataSource
) -> Player | Move | GameStateError:
    match (
        request_data[DATA_KEY].get(RELATIONSHIPS_KEY),
        request_data[DATA_KEY].get(ATTRIBUTES_KEY),
    ):
        case (None, {"newest_move": move_request_data}):
            if not existing_game_state.has_all_players:
                return GameStateError.MissingPlayer

            return parse_move_request(
                MoveUpdate(move_request_data), existing_game_state
            )
        case ({"player_o": player_update_request}, None):
            return parse_player_update_request(
                PlayerUpdate(player_update_request), existing_game_state, data_source
            )
        case ({"player_x": _}, None):
            return GameStateError.GamePlayersCannotBeUpdated

    return GameStateError.InvalidRequestBody


def parse_move_request(
    move_update: MoveUpdate, gamestate: GameState
) -> GameStateError | Move:
    match (move_update, gamestate.next_move):
        case ({"token": 1, "position": _}, XO.O) | ({"token": 0, "position": _}, XO.X):
            return GameStateError.NotYourTurn
        case (
            ({"token": 1, "position": [int(x), int(y)]}, XO.X)
            | ({"token": 0, "position": [int(x), int(y)]}, XO.O)
        ):
            if any(coord < 0 or coord > 2 for coord in (x, y)):
                return GameStateError.PositionOutOfBounds

            if gamestate.board.board[x][y] is not None:
                return GameStateError.PositionOccupied

            return Move(token=XO(move_update["token"]), position=(XCoord(x), YCoord(y)))

    return GameStateError.InvalidMoveRequest


def parse_player_update_request(
    player_update: PlayerUpdate, gamestate: GameState, data_source: DataSource
) -> GameStateError | Player:
    if (
        gamestate.players.player_x is not None
        and gamestate.players.player_o is not None
    ):
        return GameStateError.GameIsFull

    if existing_user := data_source.get_player(
        player_update.get(DATA_KEY, {}).get(ID_KEY)
    ):
        return existing_user

    return GameStateError.PlayerDoesNotExist
