from typing import Generator

import pytest

from data_source.in_memory_data_source import InMemoryDataSource, in_memory_data_source
from gamestate.data import (
    XO,
    GameResult,
    GameState,
    GamePlayers,
    Player,
    GameBoard,
    Move,
    XCoord,
    YCoord,
)


@pytest.fixture
def gamestate_zyx() -> GameState:
    return GameState(
        id="zyx",
        players=GamePlayers(player_x=Player(name="Joe", id="abce"), player_o=None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
        next_move=XO.O,
        newest_move=Move(token=XO.X, position=(XCoord(0), YCoord(0))),
        game_result=GameResult.Pending,
    )


@pytest.fixture
def gamestate_abcd() -> GameState:
    return GameState(
        id="abcd",
        players=GamePlayers(
            player_x=Player(**{"name": "Joe", "id": "abc"}),
            player_o=Player(**{"name": "Alice", "id": "def"}),
        ),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
        next_move=XO.X,
        newest_move=Move(token=XO.X, position=(XCoord(0), YCoord(0))),
        game_result=GameResult.Pending,
    )


@pytest.fixture
def gamestate_ghijkl() -> GameState:
    return GameState(
        id="ghijkl",
        players=GamePlayers(
            player_x=Player(**{"name": "Joe", "id": "abc"}),
            player_o=Player(**{"name": "Alice", "id": "def"}),
        ),
        board=GameBoard(
            board=[[XO.X, None, None], [None, None, None], [None, None, None]]
        ),
        next_move=XO.O,
        newest_move=Move(token=XO.X, position=(XCoord(0), YCoord(0))),
        game_result=GameResult.Pending,
    )


@pytest.fixture
def in_memory_data_source_fixture() -> InMemoryDataSource:
    return in_memory_data_source


@pytest.fixture
def clean_up_db() -> Generator:
    existing_data = in_memory_data_source.data
    yield
    in_memory_data_source.data = existing_data
