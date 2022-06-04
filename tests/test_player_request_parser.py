from request.data import PlayerError
from request.parsers.player_request_parser import (
    parse_player_create_request,
)


def test_parse_update_request_returns_invalid_request() -> None:
    request_data: dict = {}
    expected_result = PlayerError.InvalidRequestBody
    actual_result = parse_player_create_request(request_data)

    assert actual_result == expected_result


def test_parse_update_request_returns_wrong_resource_type() -> None:
    request_data: dict = {"data": {"type": "games"}}
    expected_result = PlayerError.WrongResourceType
    actual_result = parse_player_create_request(request_data)

    assert actual_result == expected_result


def test_parse_update_request_returns_missing_name_error() -> None:
    request_data: dict = {"data": {"type": "players", "attributes": {}}}
    expected_result = PlayerError.MissingPlayerName
    actual_result = parse_player_create_request(request_data)

    assert actual_result == expected_result


def test_parse_update_request_returns_player_with_valid_request() -> None:
    request_data: dict = {"data": {"type": "players", "attributes": {"name": "Tim"}}}
    expected_player_name = "Tim"
    actual_player_name = parse_player_create_request(request_data).name

    assert actual_player_name == expected_player_name
