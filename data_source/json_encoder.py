from json import JSONEncoder
from typing import Any

from gamestate.data import XO, GameResult


class GameStateEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            case (XO.X | XO.O) as x_or_o:
                return x_or_o.value
            case (
                GameResult.Pending
                | GameResult.XWins
                | GameResult.OWins
                | GameResult.Draw
            ) as game_result:
                return game_result.value
            case (x, y):
                return [x, y]
        return super().default(o)
