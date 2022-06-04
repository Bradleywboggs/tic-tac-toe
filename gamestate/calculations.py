import copy

from gamestate.data import (
    XO,
    GameState,
    Player,
    GamePlayers,
    Move,
    GameResult,
    UnmodifiedGameState,
    UpdatedGameState,
    GameBoard,
)


def update_players(player: Player, players: GamePlayers) -> GamePlayers:
    match (players.player_x, players.player_o):
        case (None, existing_player):
            return GamePlayers(player, existing_player)
        case (existing_player, None):
            return GamePlayers(existing_player, player)
    return players


def update_gameboard(move: Move, gameboard: GameBoard) -> GameBoard:
    (x, y), board = move.position, copy.deepcopy(gameboard.board)
    board[x][y] = move.token
    return GameBoard(board=board)


def determine_game_result(gameboard: GameBoard) -> GameResult:
    match gameboard.board:
        case (
            [[XO.X, XO.X, XO.X], *_]
            | [_, [XO.X, XO.X, XO.X], _]
            | [_, _, [XO.X, XO.X, XO.X]]
            | [[XO.X, _, _], [_, XO.X, _], [_, _, XO.X]]
            | [[_, _, XO.X], [_, XO.X, _], [XO.X, _, _]]
            | [[XO.X, *_], [XO.X, *_], [XO.X, *_]]
            | [[_, XO.X, _], [_, XO.X, _], [_, XO.X, _]]
            | [[_, _, XO.X], [_, _, XO.X], [_, _, XO.X]]
        ):
            return GameResult.XWins
        case (
            [[XO.O, XO.O, XO.O], *_]
            | [_, [XO.O, XO.O, XO.O], _]
            | [_, _, [XO.O, XO.O, XO.O]]
            | [[XO.O, _, _], [_, XO.O, _], [_, _, XO.O]]
            | [[_, _, XO.O], [_, XO.O, _], [XO.O, _, _]]
            | [[XO.O, *_], [XO.O, *_], [XO.O, *_]]
            | [[_, XO.O, _], [_, XO.O, _], [_, XO.O, _]]
            | [[_, _, XO.O], [_, _, XO.O], [_, _, XO.O]]
        ):
            return GameResult.OWins
        case _ if gameboard.is_full:
            return GameResult.Draw

    return GameResult.Pending


def update_gamestate(
    update_value: Player | GamePlayers | Move, gamestate: GameState
) -> UnmodifiedGameState | UpdatedGameState:
    if gamestate.game_result != GameResult.Pending:
        return UnmodifiedGameState(gamestate)

    match update_value:
        case Player(_) as player:
            return UpdatedGameState(
                GameState(
                    id=gamestate.id,
                    newest_move=gamestate.newest_move,
                    next_move=gamestate.next_move,
                    game_result=gamestate.game_result,
                    players=update_players(player, gamestate.players),
                    board=gamestate.board,
                )
            )
        case GamePlayers(_, _) as new_players:
            match gamestate.players:
                case GamePlayers(None, None):
                    return UpdatedGameState(
                        GameState(
                            id=gamestate.id,
                            newest_move=gamestate.newest_move,
                            next_move=gamestate.next_move,
                            game_result=gamestate.game_result,
                            players=new_players,
                            board=gamestate.board,
                        )
                    )
                case _:
                    return UnmodifiedGameState(gamestate)

        case Move(token, _) as move:
            updated_board = update_gameboard(move, gamestate.board)
            if updated_board == gamestate.board:
                return UnmodifiedGameState(gamestate)

            return UpdatedGameState(
                GameState(
                    id=gamestate.id,
                    newest_move=move,
                    next_move=XO.O if token == XO.X else XO.X,
                    game_result=determine_game_result(updated_board),
                    players=gamestate.players,
                    board=updated_board,
                )
            )
    return UnmodifiedGameState(gamestate)
