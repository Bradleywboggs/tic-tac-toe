from typing import Optional

import pytest
from fastapi import status
from gamestate.data import (
    GameState,
    Player,
    GameBoard,
    XO,
    Move,
    XCoord,
    YCoord,
    GamePlayers,
    GameResult,
)
from request.data import GameStateError
from response.data import Status
from response.game_response_handler import GameResponse


def test_game_to_response_new_game_returns_correct_response_data() -> None:
    game_state = GameState.from_player(Player(id="abc", name="Joe"), game_id="abcdef")
    expected_response_data = {
        "data": {
            "id": "abcdef",
            "type": "games",
            "attributes": {
                "board": [
                    [None, None, None],
                    [None, None, None],
                    [None, None, None],
                ],
                "next_move": 1,
                "newest_move": None,
                "game_result": "pending",
            },
            "relationships": {
                "player_x": {
                    "data": {"id": "abc", "type": "players"},
                    "links": {
                        "self": "http://localhost:8000/api/players/abc",
                    },
                },
                "player_o": None,
            },
        },
        "links": {"self": "http://localhost:8000/api/games/abcdef"},
    }

    actual_response_data = GameResponse(base_url="http://localhost:8000").to_response(
        game_state
    )

    assert actual_response_data == (200, expected_response_data)


def test_game_to_response_existing_game_returns_correct_response_data() -> None:
    game_state = GameState(
        id="abcdef",
        board=GameBoard(
            board=[[XO.O, XO.X, XO.O], [XO.X, XO.O, XO.X], [XO.O, None, None]]
        ),
        next_move=XO.X,
        newest_move=Move(token=XO.O, position=(XCoord(2), YCoord(0))),
        players=GamePlayers(
            player_x=Player(id="abc", name="Joe"),
            player_o=Player(id="def", name="Alice"),
        ),
        game_result=GameResult.Pending,
    )
    expected_response_data = {
        "data": {
            "id": "abcdef",
            "type": "games",
            "attributes": {
                "board": [
                    [0, 1, 0],
                    [1, 0, 1],
                    [0, None, None],
                ],
                "next_move": 1,
                "newest_move": {"token": 0, "position": [2, 0]},
                "game_result": "pending",
            },
            "relationships": {
                "player_x": {
                    "data": {"id": "abc", "type": "players"},
                    "links": {
                        "self": "http://localhost:8000/api/players/abc",
                    },
                },
                "player_o": {
                    "data": {"id": "def", "type": "players"},
                    "links": {
                        "self": "http://localhost:8000/api/players/def",
                    },
                },
            },
        },
        "links": {"self": "http://localhost:8000/api/games/abcdef"},
    }

    actual_response_data = GameResponse(base_url="http://localhost:8000").to_response(
        game_state
    )

    assert actual_response_data == (200, expected_response_data)


@pytest.mark.parametrize(
    ("error", "status_code", "pointer", "detail"),
    [
        (
            GameStateError.InvalidRequestBody,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data",
            GameStateError.InvalidRequestBody.value,
        ),
        (
            GameStateError.WrongResourceType,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/type",
            GameStateError.WrongResourceType.value,
        ),
        (
            GameStateError.GameNotFound,
            Status(status.HTTP_404_NOT_FOUND),
            "/data/id",
            GameStateError.GameNotFound.value,
        ),
        (
            GameStateError.GameIdConflict,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/id",
            GameStateError.GameIdConflict.value,
        ),
        (
            GameStateError.GameIsOver,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/attributes/game_result",
            GameStateError.GameIsOver.value,
        ),
        (
            GameStateError.MissingPlayer,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/relationships/player_o",
            GameStateError.MissingPlayer.value,
        ),
        (
            GameStateError.GamePlayersCannotBeUpdated,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/relationships/player_x",
            GameStateError.GamePlayersCannotBeUpdated.value,
        ),
        (
            GameStateError.GameIsFull,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/relationships/player_o",
            GameStateError.GameIsFull.value,
        ),
        (
            GameStateError.PlayerDoesNotExist,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/relationships/player_o",
            GameStateError.PlayerDoesNotExist.value,
        ),
        (
            GameStateError.PositionOccupied,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/attributes/newest_move/position",
            GameStateError.PositionOccupied.value,
        ),
        (
            GameStateError.InvalidMoveRequest,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/attributes/newest_move",
            GameStateError.InvalidMoveRequest.value,
        ),
        (
            GameStateError.PositionOutOfBounds,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/attributes/newest_move/position",
            GameStateError.PositionOutOfBounds.value,
        ),
        (
            GameStateError.NotYourTurn,
            Status(status.HTTP_400_BAD_REQUEST),
            "/data/attributes/newest_move/token",
            GameStateError.NotYourTurn.value,
        ),
        (
            GameStateError.MissingUserIdHeader,
            Status(status.HTTP_401_UNAUTHORIZED),
            None,
            GameStateError.MissingUserIdHeader.value,
        ),
    ],
)
def test_game_to_response_returns_correct_error_response(
    error: GameStateError,
    status_code: Status,
    pointer: Optional[str],
    detail: str,
) -> None:
    expected_response = (
        status_code,
        {
            "errors": [
                {
                    # "title": detail,
                    "detail": detail,
                    "status": str(status_code),
                    "source": {
                        "pointer": pointer,
                    },
                }
            ]
        },
    )

    actual_repsonse = GameResponse(base_url="http://localhost:8000").to_response(error)

    assert actual_repsonse == expected_response
