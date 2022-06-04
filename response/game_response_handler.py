from typing import Optional

from gamestate.data import GameState, Player, GameBoard, Move
from fastapi import status

from request.data import GameStateError
from response.data import Status


class GameResponse:
    error_map: dict[GameStateError, dict[str, str | Status | None]] = {
        GameStateError.InvalidRequestBody: {
            "pointer": "/data",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.WrongResourceType: {
            "pointer": "/data/type",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.GameNotFound: {
            "pointer": "/data/id",
            "status": Status(status.HTTP_404_NOT_FOUND),
        },
        GameStateError.GameIdConflict: {
            "pointer": "/data/id",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.GameIsOver: {
            "pointer": "/data/attributes/game_result",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.MissingPlayer: {
            "pointer": "/data/relationships/player_o",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.GamePlayersCannotBeUpdated: {
            "pointer": "/data/relationships/player_x",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.GameIsFull: {
            "pointer": "/data/relationships/player_o",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.PlayerDoesNotExist: {
            "pointer": "/data/relationships/player_o",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.PositionOccupied: {
            "pointer": "/data/attributes/newest_move/position",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.InvalidMoveRequest: {
            "pointer": "/data/attributes/newest_move",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.PositionOutOfBounds: {
            "pointer": "/data/attributes/newest_move/position",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.NotYourTurn: {
            "pointer": "/data/attributes/newest_move/token",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        GameStateError.MissingUserIdHeader: {
            "pointer": None,
            "status": Status(status.HTTP_401_UNAUTHORIZED),
        },
    }

    def __init__(self, base_url: str):
        self.base_url = base_url

    def to_response(
        self, response_data: GameState | GameStateError
    ) -> tuple[Status, dict]:
        if isinstance(response_data, GameState):
            return (
                Status(status.HTTP_200_OK),
                {
                    "data": self.to_game_state_response(response_data),
                    "links": {"self": f"{self.base_url}/api/games/{response_data.id}"},
                },
            )
        else:
            error = response_data
            return (  # type: ignore
                self.error_map[error]["status"],
                self.gamestate_error_to_response(error),
            )

    def gameplayer_to_response(self, player: Optional[Player]) -> Optional[dict]:
        if player is None:
            return None
        return {
            "data": {"type": "players", "id": player.id},
            "links": {"self": f"{self.base_url}/api/players/{player.id}"},
        }

    @staticmethod
    def gameboard_to_response(gameboard: GameBoard) -> list:
        int_board = []
        for row in gameboard.board:
            int_row: list[Optional[int]] = []
            for col in row:
                if col is None:
                    int_row.append(col)
                else:
                    int_row.append(col.value)
            int_board.append(int_row)
        return int_board

    @staticmethod
    def newest_move_to_response(newest_move: Optional[Move]) -> Optional[dict]:
        if newest_move is None:
            return None

        return {
            "token": newest_move.token.value,
            "position": list(newest_move.position),
        }

    def gamestate_error_to_response(self, error: GameStateError) -> dict:
        return {
            "errors": [
                {
                    "detail": error.value,
                    # "title": error.value,
                    "source": {"pointer": self.error_map[error]["pointer"]},
                    "status": str(self.error_map[error]["status"]),
                }
            ]
        }

    def to_game_state_response(self, response_data: GameState) -> dict:
        return {
            "id": response_data.id,
            "type": "games",
            "attributes": {
                "board": self.gameboard_to_response(response_data.board),
                "next_move": response_data.next_move.value,
                "newest_move": self.newest_move_to_response(response_data.newest_move),
                "game_result": response_data.game_result.value,
            },
            "relationships": {
                "player_x": self.gameplayer_to_response(response_data.players.player_x),
                "player_o": self.gameplayer_to_response(response_data.players.player_o),
            },
        }
