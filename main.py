import os

from fastapi import FastAPI, Body, Depends, Header
from redis.client import Redis
from starlette.responses import JSONResponse

import bootstrap
from request.handlers.game_request_handlers import (
    GameStateUpdateHandler,
    GameCreateHandler,
    GameGetHandler,
    GamesGetHandler,
)
from request.handlers.player_request_handlers import PlayerRequestHandler

app = FastAPI()


@app.get("/api/players/{player_id}")
def get_player(
    player_id: str,
    request_handler: PlayerRequestHandler = Depends(bootstrap.player_request_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(player_id)
    return JSONResponse(content=response_data, status_code=status_code)


@app.get("/api/players")
def get_players(
    request_handler: PlayerRequestHandler = Depends(bootstrap.player_request_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(None)
    return JSONResponse(content=response_data, status_code=status_code)


@app.get("/api/players/{player_id}/games")
def get_player_games(
    player_id: str,
    request_handler: GamesGetHandler = Depends(bootstrap.games_get_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(player_id)
    return JSONResponse(content=response_data, status_code=status_code)


@app.post("/api/players")
def create_player(
    data: dict = Body(),
    request_handler: PlayerRequestHandler = Depends(bootstrap.player_request_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(data)
    return JSONResponse(content=response_data, status_code=status_code)


@app.get("/api/games")
def get_games(
    request_handler: GamesGetHandler = Depends(bootstrap.games_get_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(None)
    return JSONResponse(content=response_data, status_code=status_code)


@app.get("/api/games/{game_id}")
def get_game(
    game_id: str,
    request_handler: GameGetHandler = Depends(bootstrap.game_get_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(game_id)
    return JSONResponse(content=response_data, status_code=status_code)


@app.post("/api/games")
def create_game(
    data: dict = Body(),
    user_id: str | None = Header(default=None),
    request_handler: GameCreateHandler = Depends(bootstrap.game_create_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(user_id, data)
    return JSONResponse(content=response_data, status_code=status_code)


@app.patch("/api/games/{game_id}")
def update_game(
    game_id: str,
    data: dict = Body(),
    request_handler: GameStateUpdateHandler = Depends(bootstrap.game_update_handler),
) -> JSONResponse:
    status_code, response_data = request_handler.handle_request(game_id, data)
    return JSONResponse(content=response_data, status_code=status_code)
