from data_source.data_source import DataSource
from gamestate.data import Player
from request.data import PlayerError, GameStateError

PLAYERS_TYPE = "players"


def parse_player_create_request(request_data: dict) -> PlayerError | Player:
    if not request_data.get("data") or not isinstance(request_data["data"], dict):
        return PlayerError.InvalidRequestBody
    if request_data["data"].get("type") != PLAYERS_TYPE:
        return PlayerError.WrongResourceType

    match request_data["data"].get("attributes"):
        case {"name": str(name)}:
            return Player.from_name(name=name)
        case _:
            return PlayerError.MissingPlayerName
