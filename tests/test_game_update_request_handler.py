from starlette import status

from data_source.in_memory_data_source import InMemoryDataSource
from request.handlers.game_request_handlers import GameStateUpdateHandler
from response.data import Status
from response.game_response_handler import GameResponse


def test_request_handler_parses_input_and_returns_tuple_status_and_response_object_happy_path(
    in_memory_data_source_fixture: InMemoryDataSource, clean_up_db: None
) -> None:
    path_var_id = "ghijkl"
    request_data = {
        "data": {
            "id": "ghijkl",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 0, "position": [0, 1]},
            },
        }
    }
    handler = GameStateUpdateHandler(
        data_source=in_memory_data_source_fixture,
        response_handler=GameResponse(base_url="http://localhost:8000"),
    )
    actual_result = handler.handle_request(path_var_id, request_data)
    expected_result: tuple[Status, dict] = (
        Status(status.HTTP_200_OK),
        {
            "data": {
                "attributes": {
                    "board": [[1, 0, None], [None, None, None], [None, None, None]],
                    "game_result": "pending",
                    "newest_move": {"position": [0, 1], "token": 0},
                    "next_move": 1,
                },
                "id": "ghijkl",
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
            },
            "links": {"self": "http://localhost:8000/api/games/ghijkl"},
        },
    )

    assert actual_result == expected_result


def test_request_handler_parses_input_and_returns_tuple_status_and_response_object_error(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    path_var_id = "not_here"
    request_data = {
        "data": {
            "id": "not_here",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 0, "position": [0, 1]},
            },
        }
    }
    handler = GameStateUpdateHandler(
        data_source=in_memory_data_source_fixture,
        response_handler=GameResponse(base_url="http://localhost:8000"),
    )
    actual_result = handler.handle_request(path_var_id, request_data)
    expected_result: tuple[Status, dict] = Status(status.HTTP_404_NOT_FOUND), {
            "errors": [
                {
                    "detail": "Game not found",
                    "source": {"pointer": "/data/id"},
                    "status": "404",
                    # "title": "Game not found",
                }
            ]
        }

    assert actual_result == expected_result
