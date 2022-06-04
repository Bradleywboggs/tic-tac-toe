from starlette.testclient import TestClient

from main import app

client: TestClient = TestClient(app)


def test_update_game_bad_request() -> None:
    response = client.patch(
        "/api/games/not_here", json={"data": {"type": "games", "id": "not_here"}}
    )
    assert (response.status_code, response.json()) == (
        404,
        {
            "errors": [
                {
                    "detail": "Game not found",
                    "source": {"pointer": "/data/id"},
                    "status": "404",
                    # "title": "Game not found",
                }
            ]
        },
    )


def test_update_game_happy_path(clean_up_db: None) -> None:
    response = client.patch(
        "/api/games/abcd",
        json={
            "data": {
                "type": "games",
                "id": "abcd",
                "attributes": {"newest_move": {"token": 1, "position": [0, 2]}},
            }
        },
    )
    assert (response.status_code, response.json()) == (
        200,
        {
            "data": {
                "attributes": {
                    "board": [[None, None, 1], [None, None, None], [None, None, None]],
                    "game_result": "pending",
                    "newest_move": {"position": [0, 2], "token": 1},
                    "next_move": 0,
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
            },
            "links": {"self": "http://localhost:8000/api/games/abcd"},
        },
    )


def test_create_game_no_header() -> None:
    response = client.post("/api/games", json={"data": {"type": "games"}})
    assert (response.status_code, response.json()) == (
        401,
        {
            "errors": [
                {
                    "detail": "User-Id header must be passed",
                    "source": {"pointer": None},
                    "status": "401",
                    # "title": "User-Id header must be passed",
                }
            ]
        },
    )


def test_create_game_happy_path(clean_up_db: None) -> None:
    response = client.post(
        "/api/games", json={"data": {"type": "games"}}, headers={"User-Id": "abc"}
    )

    deterministic_id = "qwertyuio"
    response_data = response.json()
    response_data["data"]["id"] = deterministic_id
    response_data["links"][
        "self"
    ] = f"http://localhost:8000/api/games/{deterministic_id}"

    assert (response.status_code, response_data) == (
        201,
        {
            "data": {
                "attributes": {
                    "board": [
                        [None, None, None],
                        [None, None, None],
                        [None, None, None],
                    ],
                    "game_result": "pending",
                    "newest_move": None,
                    "next_move": 1,
                },
                "id": "qwertyuio",
                "relationships": {
                    "player_o": None,
                    "player_x": {
                        "data": {"id": "abc", "type": "players"},
                        "links": {"self": "http://localhost:8000/api/players/abc"},
                    },
                },
                "type": "games",
            },
            "links": {"self": "http://localhost:8000/api/games/qwertyuio"},
        },
    )


def test_get_game_not_found() -> None:
    response = client.get("/api/games/not_here")
    assert (response.status_code, response.json()) == (
        404,
        {
            "errors": [
                {
                    "detail": "Game not found",
                    "source": {"pointer": "/data/id"},
                    "status": "404",
                    # "title": "Game not found",
                }
            ]
        },
    )
