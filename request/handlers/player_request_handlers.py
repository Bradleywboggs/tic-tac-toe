from typing import Any

from data_source.data_source import DataSource
from gamestate.data import Player
from request.data import PlayerError
from response.data import Status
from response.player_response_handler import PlayerResponse
from request.parsers.player_request_parser import parse_player_create_request
from response.players_response_handler import PlayersResponse


class PlayerRequestHandler:
    def __init__(self, data_source: DataSource, response_handler: PlayerResponse):
        self.response_handler = response_handler
        self.data_source = data_source

    def handle_request(self, request_data: dict | str | None) -> tuple[Status, dict]:
        match request_data:
            case None:
                all_players = self.data_source.get_players()
                return PlayersResponse(self.response_handler).to_response(all_players)
            case str(_) as user_id:
                if player := self.data_source.get_player(user_id):
                    return self.response_handler.to_response(player)  # type: ignore
                return self.response_handler.to_response(PlayerError.PlayerNotFound)  # type: ignore
            case _:
                new_player: PlayerError | Player = parse_player_create_request(
                    request_data
                )
                if isinstance(new_player, PlayerError):
                    return self.response_handler.to_response(new_player)  # type: ignore

                self.data_source.add_player(new_player)
                return self.response_handler.to_response(new_player)  # type: ignore
