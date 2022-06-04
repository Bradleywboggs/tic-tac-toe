from enum import Enum
from typing import NewType

PlayerUpdate = NewType("PlayerUpdate", dict)
MoveUpdate = NewType("MoveUpdate", dict)

Links = NewType("Links", list[dict])
Relationships = NewType("Relationships", list[dict])


class PlayerError(Enum):
    PlayerNotFound = "PlayerNotFound"
    MissingPlayerName = "Player name is required"
    InvalidRequestBody = "Request body not valid."
    WrongResourceType = "Wrong or Missing Resource Type. Type should be 'players'."


class GameStateError(Enum):
    MissingUserIdHeader = "User-Id header must be passed"
    InvalidRequestBody = "Request body not valid."
    WrongResourceType = "Wrong or Missing Resource Type. Type should be 'games'."
    GameNotFound = "Game not found"
    GameIdConflict = "Path Id does not match Body Id or Body Id is missing"
    GameIsOver = "Game is over"
    MissingPlayer = "Player O is Missing"
    GamePlayersCannotBeUpdated = "Game Players Cannot be Updated. Start a new game."
    GameIsFull = "Game Is Full. No players can be changed or added. Start a new game."
    PlayerDoesNotExist = "Player Does not Exist. Please register at /api/players."
    PositionOccupied = "Board Position is already occupied. Select an empty position."
    InvalidMoveRequest = 'Invalid Move Request: Your "newest_move" value should look something like {"token": 1, "position": [2, 1]}'
    PositionOutOfBounds = "Position Out of GameBoard Bounds."
    NotYourTurn = "Wrong Token passed in Move."
