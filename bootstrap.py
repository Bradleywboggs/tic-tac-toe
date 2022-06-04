import os

from container import Env, container
from request.handlers.game_request_handlers import (
    GameCreateHandler,
    GameStateUpdateHandler,
    GameGetHandler,
    GamesGetHandler,
)
from request.handlers.player_request_handlers import PlayerRequestHandler
from response.game_response_handler import GameResponse
from response.games_response_handler import GamesResponse
from response.player_response_handler import PlayerResponse


def game_update_handler() -> GameStateUpdateHandler:
    env = Env(os.environ.get("ENV", "test"))
    return GameStateUpdateHandler(
        data_source=container.data_sources[env](),
        response_handler=GameResponse(base_url=container.base_urls[env].value),
    )


def game_create_handler() -> GameCreateHandler:
    env = Env(os.environ.get("ENV", "test"))
    return GameCreateHandler(
        data_source=container.data_sources[env](),
        response_handler=GameResponse(base_url=container.base_urls[env].value),
    )


def game_get_handler() -> GameGetHandler:
    env = Env(os.environ.get("ENV", "test"))
    return GameGetHandler(
        data_source=container.data_sources[env](),
        response_handler=GameResponse(base_url=container.base_urls[env].value),
    )


def games_get_handler() -> GamesGetHandler:
    env = Env(os.environ.get("ENV", "test"))
    return GamesGetHandler(
        data_source=container.data_sources[env](),
        response_handler=GamesResponse(
            game_response=GameResponse(base_url=container.base_urls[env].value)
        ),
    )


def player_request_handler() -> PlayerRequestHandler:
    env = Env(os.environ.get("ENV", "test"))
    return PlayerRequestHandler(
        data_source=container.data_sources[env](),
        response_handler=PlayerResponse(base_url=container.base_urls[env].value),
    )
