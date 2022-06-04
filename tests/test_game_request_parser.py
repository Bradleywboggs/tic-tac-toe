import json
from dataclasses import asdict

import pytest

from data_source.in_memory_data_source import InMemoryDataSource
from data_source.json_encoder import GameStateEncoder
from gamestate.data import (
    GameState,
    Move,
    XO,
    XCoord,
    YCoord,
    Player,
)
from request.data import GameStateError
from request.parsers.game_request_parser import (
    parse_player_from_game_create_request,
    parse_update_request,
    validate_existing_game,
)


def test_parse_update_request_returns_invalid_request(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    game_id = "abcd"
    request_data: dict = {}
    expected_result = GameStateError.InvalidRequestBody
    actual_result = validate_existing_game(
        request_data, game_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_wrong_request_type_is_not_games(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    game_id = "abcd"
    request_data = {
        "data": {
            "type": "something_not_games",
        }
    }
    expected_result = GameStateError.WrongResourceType
    actual_result = validate_existing_game(
        request_data, game_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_game_not_found_if_game_id_not_found_in_data_source(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    game_id = "not_existing_game"
    request_data = {
        "data": {
            "id": "not_existing_game",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [0, 1]},
            },
        }
    }
    expected_result = GameStateError.GameNotFound
    actual_result = validate_existing_game(
        request_data, game_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_game_id_conflict_error_if_path_var_id_doesnt_match_request_id(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    game_id = "abcd"
    request_data = {
        "data": {
            "id": "not_existing_game",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [0, 1]},
            },
        }
    }
    expected_result = GameStateError.GameIdConflict
    actual_result = validate_existing_game(
        request_data, game_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_missing_player_when_move_made_without_full_game(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_zyx: GameState
) -> None:
    request_data = {
        "data": {
            "id": "zyx",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [0, 1]},
            },
        }
    }
    expected_result = GameStateError.MissingPlayer
    actual_result = parse_update_request(
        request_data, gamestate_zyx, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_xmove_when_xs_turn(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_abcd: GameState
) -> None:
    request_data = {
        "data": {
            "id": "abcd",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [0, 1]},
            },
        }
    }
    expected_result = Move(token=XO.X, position=(XCoord(0), YCoord(1)))
    actual_result = parse_update_request(
        request_data, gamestate_abcd, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_o_move_if_its_os_turn(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_ghijkl: GameState
) -> None:
    request_data = {
        "data": {
            "id": "ghijkl",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 0, "position": [0, 1]},
            },
        }
    }
    expected_result = Move(token=XO.O, position=(XCoord(0), YCoord(1)))
    actual_result = parse_update_request(
        request_data, gamestate_ghijkl, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_not_your_turn_if_wrong_token_sent(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_abcd: GameState
) -> None:
    request_data = {
        "data": {
            "id": "abcd",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 0, "position": [0, 1]},
            },
        }
    }
    expected_result = GameStateError.NotYourTurn
    actual_result = parse_update_request(
        request_data, gamestate_abcd, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_position_out_of_bounds_if_coord_greater_than_2_sent(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_abcd: GameState
) -> None:
    request_data = {
        "data": {
            "id": "abcd",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [5, 2]},
            },
        }
    }
    expected_result = GameStateError.PositionOutOfBounds
    actual_result = parse_update_request(
        request_data, gamestate_abcd, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_position_out_of_bounds_if_coord_less_than_0_sent(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_abcd: GameState
) -> None:
    request_data = {
        "data": {
            "id": "abcd",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 1, "position": [2, -1]},
            },
        }
    }
    expected_result = GameStateError.PositionOutOfBounds
    actual_result = parse_update_request(
        request_data, gamestate_abcd, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_returns_position_occupied_if_position_is_already_set_on_board(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_ghijkl: GameState
) -> None:
    request_data = {
        "data": {
            "id": "ghijkl",
            "type": "games",
            "attributes": {
                "newest_move": {"token": 0, "position": [0, 0]},
            },
        }
    }
    expected_result = GameStateError.PositionOccupied
    actual_result = parse_update_request(
        request_data, gamestate_ghijkl, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_body_to_player_returns_player_when_player_exists(
    in_memory_data_source_fixture: InMemoryDataSource,
    gamestate_zyx: GameState,
    clean_up_db: None,
) -> None:
    update_player_request_body = {
        "data": {
            "type": "games",
            "id": "zyx",
            "relationships": {"player_o": {"data": {"type": "players", "id": "abc"}}},
        }
    }

    expected_result = Player(name="Joe", id="abc")
    actual_result = parse_update_request(
        update_player_request_body, gamestate_zyx, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_body_to_player_returns_player_does_not_exist_if_player_not_registered(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_zyx: GameState
) -> None:
    update_player_request_body = {
        "data": {
            "type": "games",
            "id": "zyx",
            "relationships": {"player_o": {"data": {"type": "players", "id": "ghi"}}},
        }
    }

    expected_result = GameStateError.PlayerDoesNotExist
    actual_result = parse_update_request(
        update_player_request_body, gamestate_zyx, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_body_to_player_returns_game_is_full_if_no_slots_available(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_ghijkl: GameState
) -> None:
    update_player_request_body = {
        "data": {
            "type": "games",
            "id": "ghijkl",
            "relationships": {"player_o": {"data": {"type": "players", "id": "abc"}}},
        }
    }

    expected_result = GameStateError.GameIsFull
    actual_result = parse_update_request(
        update_player_request_body, gamestate_ghijkl, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_parse_update_request_body_to_player_returns_cannot_update_player_x(
    in_memory_data_source_fixture: InMemoryDataSource, gamestate_ghijkl: GameState
) -> None:
    update_player_request_body = {
        "data": {
            "type": "games",
            "id": "ghijkl",
            "relationships": {"player_x": {"data": {"type": "players", "id": "def"}}},
        }
    }

    expected_result = GameStateError.GamePlayersCannotBeUpdated
    actual_result = parse_update_request(
        update_player_request_body, gamestate_ghijkl, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


def test_game_state_encoder() -> None:
    gamestate = asdict(
        GameState.from_player(Player(name="Joe", id="abc"), game_id="99977d")
    )
    expected_result = {
        "board": {
            "board": [[None, None, None], [None, None, None], [None, None, None]]
        },
        "game_result": "pending",
        "id": "99977d",
        "newest_move": None,
        "next_move": 1,
        "players": {"player_o": None, "player_x": {"id": "abc", "name": "Joe"}},
    }
    actual_result = json.loads(json.dumps(gamestate, cls=GameStateEncoder))
    assert actual_result == expected_result


def test_parse_update_request_returns_game_complete_error_if_game_is_not_pending(
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    game_id = "finished_game"
    update_request_data = {
        "data": {
            "type": "games",
            "id": "finished_game",
        }
    }

    expected_result = GameStateError.GameIsOver
    actual_result = validate_existing_game(
        update_request_data, game_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result


@pytest.mark.parametrize(
    ("user_id", "expected_result"),
    [
        ("abc", Player(id="abc", name="Joe")),
        ("not_found", GameStateError.PlayerDoesNotExist),
        (None, GameStateError.MissingUserIdHeader),
    ],
)
def test_parse_player_from_request_for_create_game_request(
    user_id: str | None,
    expected_result: Player | GameStateError,
    in_memory_data_source_fixture: InMemoryDataSource,
) -> None:
    actual_result = parse_player_from_game_create_request(
        user_id, in_memory_data_source_fixture
    )

    assert actual_result == expected_result
