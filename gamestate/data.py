import uuid
from enum import Enum
from typing import TypeAlias, Optional, NewType
from dataclasses import dataclass


class XO(Enum):
    O = 0
    X = 1


Name: TypeAlias = str
GameId: TypeAlias = str


@dataclass
class Player:
    id: str
    name: Name

    @classmethod
    def from_name(cls, name: str) -> "Player":
        return cls(name=name, id=str(uuid.uuid4())[0:6])


@dataclass
class GamePlayers:
    player_x: Optional[Player]
    player_o: Optional[Player]


@dataclass
class GameBoard:
    board: list[list[Optional[XO]]]

    @classmethod
    def new(cls) -> "GameBoard":
        return cls(board=[[None, None, None], [None, None, None], [None, None, None]])

    @property
    def is_full(self) -> bool:
        return (
            None not in self.board[0]
            and None not in self.board[1]
            and None not in self.board[2]
        )


XCoord = NewType("XCoord", int)
YCoord = NewType("YCoord", int)


@dataclass
class Move:
    """
    A Move is guaranteed to be within the bounds of the board and
    cannot conflict with existing X's or O's on the board.
    """

    token: XO
    position: tuple[XCoord, YCoord]


class GameResult(Enum):
    Pending = "pending"
    OWins = "o_wins"
    XWins = "x_wins"
    Draw = "draw"


@dataclass
class GameState:
    id: str
    players: GamePlayers
    board: GameBoard
    next_move: XO
    newest_move: Optional[Move]
    game_result: GameResult

    @classmethod
    def from_player(cls, player: Player, game_id: Optional[str] = None) -> "GameState":
        new_id = game_id or str(uuid.uuid4())[0:6]
        return cls(
            id=new_id,
            players=GamePlayers(player, None),
            board=GameBoard.new(),
            next_move=XO.X,
            newest_move=None,
            game_result=GameResult.Pending,
        )

    @property
    def game_is_over(self) -> bool:
        return self.game_result != GameResult.Pending

    @property
    def has_all_players(self) -> bool:
        return self.players.player_x is not None and self.players.player_o is not None


UnmodifiedGameState = NewType("UnmodifiedGameState", GameState)
UpdatedGameState = NewType("UpdatedGameState", GameState)
