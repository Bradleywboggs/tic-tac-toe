from typing import Optional

import pytest

from gamestate.data import Player
from request.data import PlayerError
from response.data import Status
from response.player_response_handler import PlayerResponse


@pytest.fixture
def player_response() -> PlayerResponse:
    return PlayerResponse(base_url="http://localhost:8000")


@pytest.mark.parametrize(
    ("error", "status", "detail", "pointer"),
    [
        (
            PlayerError.InvalidRequestBody,
            Status(400),
            PlayerError.InvalidRequestBody.value,
            "/data",
        ),
        (
            PlayerError.WrongResourceType,
            Status(400),
            PlayerError.WrongResourceType.value,
            "/data/type",
        ),
        (
            PlayerError.MissingPlayerName,
            Status(400),
            PlayerError.MissingPlayerName.value,
            "/data/attributes/name",
        ),
    ],
)
def test_player_response_returns_error_response(
    error: PlayerError,
    status: Status,
    detail: str,
    pointer: Optional[str],
    player_response: PlayerResponse,
) -> None:
    actual_result = player_response.to_response(error)
    expected_result = (
        status,
        {
            "errors": [
                {
                    "detail": detail,
                    # "title": detail,
                    "source": {"pointer": pointer},
                    "status": str(status),
                }
            ]
        },
    )
    assert actual_result == expected_result


def test_player_response_returns_happy_path_response(
    player_response: PlayerResponse,
) -> None:
    player = Player(name="Nancy", id="bojekd")
    actual_result = player_response.to_response(player)
    expected_result = (
        200,
        {
            "data": {
                "id": "bojekd",
                "type": "players",
                "attributes": {"name": "Nancy"},
            },
            "links": {"self": "http://localhost:8000/api/players/bojekd"},
        },
    )

    assert actual_result == expected_result
