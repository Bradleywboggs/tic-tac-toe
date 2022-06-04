import abc

from starlette import status

from data_source.data_source import DataSource
from gamestate.calculations import update_gamestate
from gamestate.data import Move
from gamestate.data import Player, GameState
from request.data import GameStateError
from request.parsers.game_request_parser import (
    parse_player_from_game_create_request,
    parse_update_request,
    validate_existing_game,
)

from response.data import Status
from response.game_response_handler import GameResponse
from response.games_response_handler import GamesResponse


class GameCreateHandler:
    def __init__(self, data_source: DataSource, response_handler: GameResponse):
        self.response_handler = response_handler
        self.data_source = data_source

    def handle_request(
        self, user_id: str | None, request_data: dict
    ) -> tuple[Status, dict]:
        parse_result: GameStateError | Player = parse_player_from_game_create_request(
            user_id, self.data_source
        )
        if isinstance(parse_result, GameStateError):
            return self.response_handler.to_response(parse_result)

        new_gamestate = GameState.from_player(parse_result)
        self.data_source.update_game(new_gamestate)

        _, response_data = self.response_handler.to_response(new_gamestate)
        return Status(status.HTTP_201_CREATED), response_data


class GameStateUpdateHandler:
    def __init__(self, data_source: DataSource, response_handler: GameResponse):
        self.response_handler = response_handler
        self.data_source = data_source

    def handle_request(
        self, path_var_id: str, request_data: dict
    ) -> tuple[Status, dict]:
        existing_game: GameStateError | GameState = validate_existing_game(
            request_data, path_var_id, self.data_source
        )

        if isinstance(existing_game, GameStateError):
            return self.response_handler.to_response(existing_game)

        parsed = parse_update_request(request_data, existing_game, self.data_source)
        match parsed:
            case (Player(_) | Move(_)) as valid_update:
                new_gamestate = update_gamestate(valid_update, existing_game)
                self.data_source.update_game(new_gamestate)
                return self.response_handler.to_response(new_gamestate)

        # error case
        return self.response_handler.to_response(parsed)


class GameGetHandler:
    def __init__(self, data_source: DataSource, response_handler: GameResponse):
        self.response_handler = response_handler
        self.data_source = data_source

    def handle_request(self, path_var_id: str) -> tuple[Status, dict]:
        existing_game: GameState | None = self.data_source.get_game(path_var_id)
        if existing_game is None:
            return self.response_handler.to_response(GameStateError.GameNotFound)
        return self.response_handler.to_response(existing_game)


class GamesGetHandler:
    def __init__(self, data_source: DataSource, response_handler: GamesResponse):
        self.response_handler = response_handler
        self.data_source = data_source

    def handle_request(self, player_id: None | str) -> tuple[Status, dict]:
        match player_id:
            case str(_):
                games = self.data_source.get_player_games(player_id)
                return self.response_handler.to_response(games)
            case _:
                all_games = self.data_source.get_games()
                return self.response_handler.to_response(all_games)
