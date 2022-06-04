import uuid
import pytest

from gamestate.calculations import (
    determine_game_result,
    update_gameboard,
    update_players,
    update_gamestate,
)
from gamestate.data import (
    GameResult,
    XO,
    GameBoard,
    Move,
    GameState,
    Player,
    GamePlayers,
    YCoord,
    XCoord,
)


# Server API
# GET /api/games - return a list f all known games
# POST /api/games : Create a new game
# GET /api/games/id : View game
# PUT /api/games/id : Update game

# -- update players
# -- PUT player
# -- take a turn: which updates the


@pytest.mark.parametrize(
    ("gameboard", "expected_result"),
    [
        (
            GameBoard(
                board=[[XO.X, XO.X, XO.X], [None, None, None], [None, None, None]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, XO.O, None], [XO.X, XO.X, XO.X], [None, None, None]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, None, None], [None, None, None], [XO.X, XO.X, XO.X]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, None, None], [None, None, None], [XO.X, XO.X, XO.X]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[XO.X, None, None], [None, XO.X, None], [XO.X, XO.O, XO.X]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, None, XO.X], [None, XO.X, None], [XO.X, XO.O, XO.X]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[XO.X, None, XO.O], [XO.X, XO.X, None], [XO.X, XO.O, XO.O]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, XO.X, None], [None, XO.X, None], [None, XO.X, None]]
            ),
            GameResult.XWins,
        ),
        (
            GameBoard(
                board=[[None, None, XO.X], [None, None, XO.X], [None, None, XO.X]]
            ),
            GameResult.XWins,
        ),
    ],
)
def test_determine_game_result_returns_x_wins_for_all_gameboards_where_x_wins(
    gameboard: GameBoard, expected_result: GameResult
) -> None:
    actual_result = determine_game_result(gameboard)
    assert actual_result == expected_result


@pytest.mark.parametrize(
    ("gameboard", "expected_result"),
    [
        (
            GameBoard(
                board=[[XO.O, XO.O, XO.O], [None, None, None], [None, None, None]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, XO.O, None], [XO.O, XO.O, XO.O], [None, None, None]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, None, None], [None, None, None], [XO.O, XO.O, XO.O]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, None, None], [None, None, None], [XO.O, XO.O, XO.O]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[XO.O, None, None], [None, XO.O, None], [XO.O, XO.O, XO.O]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, None, XO.O], [None, XO.O, None], [XO.O, XO.O, XO.O]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[XO.O, None, XO.O], [XO.O, XO.O, None], [XO.O, XO.O, XO.O]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, XO.O, None], [None, XO.O, None], [None, XO.O, None]]
            ),
            GameResult.OWins,
        ),
        (
            GameBoard(
                board=[[None, None, XO.O], [None, None, XO.O], [None, None, XO.O]]
            ),
            GameResult.OWins,
        ),
    ],
)
def test_determine_game_result_returns_o_wins_for_all_gameboards_where_o_wins(
    gameboard: GameBoard, expected_result: GameResult
) -> None:
    actual_result = determine_game_result(gameboard)
    assert actual_result == expected_result


def test_determine_game_result_returns_pending_when_no_other_case_is_matched() -> None:
    actual_result = determine_game_result(
        GameBoard(board=[[None, None, None], [None, None, None], [None, None, None]])
    )
    assert actual_result == GameResult.Pending


def test_determine_game_result_returns_draw_when_the_game_cannot_be_won() -> None:
    actual_result = determine_game_result(
        GameBoard(board=[[XO.O, XO.O, XO.X], [XO.X, XO.X, XO.O], [XO.O, XO.X, XO.X]])
    )
    assert actual_result is GameResult.Draw


def test_update_gameboard_returns_new_gameboard_with_new_move_token_if_move_coordinate_unoccupied() -> None:
    move = Move(token=XO.O, position=(XCoord(0), YCoord(0)))
    gameboard = GameBoard(
        board=[[None, None, None], [None, None, None], [None, None, None]]
    )
    expected_new_gameboard = GameBoard(
        board=[[XO.O, None, None], [None, None, None], [None, None, None]]
    )
    actual_new_gameboard = update_gameboard(move, gameboard)
    assert actual_new_gameboard == expected_new_gameboard


def test_add_player_adds_player_when_o_position_is_available() -> None:
    existing_players = GamePlayers(player_x=Player(name="Joe", id="abc"), player_o=None)
    new_player = Player(name="Alice", id="def")

    expected_new_players = GamePlayers(
        player_x=Player(name="Joe", id="abc"),
        player_o=Player(name="Alice", id="def"),
    )
    actual_new_players = update_players(new_player, existing_players)

    assert actual_new_players == expected_new_players


def test_add_player_adds_player_when_x_position_is_available() -> None:
    existing_players = GamePlayers(None, Player(name="Joe", id="def"))
    new_player = Player(name="Alice", id="abc")

    expected_new_players = GamePlayers(
        Player(name="Alice", id="abc"),
        Player(name="Joe", id="def"),
    )
    actual_new_players = update_players(new_player, existing_players)

    assert actual_new_players == expected_new_players


def test_add_player_returns_existing_players_when_no_position_is_available() -> None:
    new_player = Player(name="Pauly", id="ghi")
    existing_players = GamePlayers(
        Player(name="Alice", id="abc"),
        Player(name="Joe", id="def"),
    )
    expected_new_players = GamePlayers(
        Player(name="Alice", id="abc"),
        Player(name="Joe", id="def"),
    )
    actual_new_players = update_players(new_player, existing_players)

    assert actual_new_players == expected_new_players


def test_update_gamestate_with_new_player_returns_same_gamestate_with_new_player_in_x_position_if_gamestate_has_no_players() -> None:
    gamestate_id = str(uuid.uuid4())[0:6]
    gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(None, None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    new_player = Player(name="Joe", id="abc")
    expected_new_gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(Player(name="Joe", id="abc"), None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    actual_new_gamestate = update_gamestate(new_player, gamestate)

    assert actual_new_gamestate == expected_new_gamestate


def test_update_gamestate_with_gameplayers_returns_same_gamestate_with_new_gameplayers_if_gamestate_has_no_players() -> None:
    gamestate_id = str(uuid.uuid4())[0:6]
    gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(None, None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    new_gameplayers = GamePlayers(
        Player(name="Joe", id="abc"), Player(name="Alice", id="def")
    )
    expected_new_gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(
            Player(name="Joe", id="abc"), Player(name="Alice", id="def")
        ),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    actual_new_gamestate = update_gamestate(new_gameplayers, gamestate)

    assert actual_new_gamestate == expected_new_gamestate


def test_update_gamestate_with_gameplayers_returns_same_gamestate_with_same_gameplayers_if_gamestate_has_any_players() -> None:
    gamestate_id = str(uuid.uuid4())[0:6]
    gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(Player(name="Joe", id="abc"), None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    new_gameplayers = GamePlayers(
        Player(name="Joe", id="abc"), Player(name="Alice", id="def")
    )
    expected_new_gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(Player(name="Joe", id="abc"), None),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    actual_new_gamestate = update_gamestate(new_gameplayers, gamestate)

    assert actual_new_gamestate == expected_new_gamestate


def test_updated_gamestate_with_move_updates_gamestate_with_updated_board_next_move_most_newest_move_if_move_is_valid() -> None:
    gamestate_id = str(uuid.uuid4())[0:6]
    gamestate = GameState(
        id=gamestate_id,
        newest_move=None,
        next_move=XO.X,
        game_result=GameResult.Pending,
        players=GamePlayers(
            Player(name="Joe", id="abc"), Player(name="Alice", id="def")
        ),
        board=GameBoard(
            board=[[None, None, None], [None, None, None], [None, None, None]]
        ),
    )
    move = Move(token=XO.X, position=(XCoord(0), YCoord(0)))
    expected_new_gamestate = GameState(
        id=gamestate_id,
        newest_move=move,
        next_move=XO.O,
        game_result=GameResult.Pending,
        players=GamePlayers(
            Player(name="Joe", id="abc"), Player(name="Alice", id="def")
        ),
        board=GameBoard(
            board=[[XO.X, None, None], [None, None, None], [None, None, None]]
        ),
    )
    actual_new_gamestate = update_gamestate(move, gamestate)

    assert actual_new_gamestate == expected_new_gamestate
