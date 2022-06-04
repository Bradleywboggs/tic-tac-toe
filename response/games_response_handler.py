from typing import List

from gamestate.data import GameState
from response.data import Status
from response.game_response_handler import GameResponse


class GamesResponse:
    def __init__(self, game_response: GameResponse):
        self.game_response = game_response

    def to_response(self, games: List[GameState]) -> tuple[Status, dict]:
        if not games:
            return Status(200), {"data": [], "links": None}  # type: ignore

        return (
            200,
            {  # type: ignore
                "data": [
                    self.game_response.to_game_state_response(game) for game in games
                ],
                "links": {
                    "self": f"{self.game_response.base_url}/api/games",
                },
                "meta": {
                    "page": 1,
                    "previous": None,
                    "next": None,
                    "count": len(games),
                },
            },
        )
