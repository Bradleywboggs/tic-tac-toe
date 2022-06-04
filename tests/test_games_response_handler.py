import pytest

from gamestate.data import (
    GameState,
)
from response.data import Status
from response.game_response_handler import GameResponse
from response.games_response_handler import GamesResponse


@pytest.fixture
def games_response() -> GamesResponse:
    return GamesResponse(game_response=GameResponse(base_url="http://localhost:8000"))


def test_games_to_reponse_returns_empty_payload_with_200_if_no_data(
    games_response: GamesResponse,
) -> None:
    games: list[GameState] = []
    expected_response_data: tuple[Status, dict] = (
        Status(200),
        {"data": [], "links": None},
    )
    actual_response_data = games_response.to_response(games)
    assert actual_response_data == expected_response_data


def test_games_to_reponse_returns_list_of_gaes_with_200_if_data(
    games_response: GamesResponse, gamestate_abcd: GameState, gamestate_zyx: GameState
) -> None:
    games = [gamestate_abcd]
    expected_response_data = (
        200,
        {
            "data": [
                {
                    "attributes": {
                        "board": [
                            [None, None, None],
                            [None, None, None],
                            [None, None, None],
                        ],
                        "game_result": "pending",
                        "newest_move": {"position": [0, 0], "token": 1},
                        "next_move": 1,
                    },
                    "id": "abcd",
                    "relationships": {
                        "player_o": {
                            "data": {"id": "def", "type": "players"},
                            "links": {"self": "http://localhost:8000/api/players/def"},
                        },
                        "player_x": {
                            "data": {"id": "abc", "type": "players"},
                            "links": {"self": "http://localhost:8000/api/players/abc"},
                        },
                    },
                    "type": "games",
                }
            ],
            "links": {"self": "http://localhost:8000/api/games"},
            "meta": {"count": 1, "next": None, "page": 1, "previous": None},
        },
    )
    actual_response_data = games_response.to_response(games)
    assert actual_response_data == expected_response_data
