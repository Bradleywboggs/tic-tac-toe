from gamestate.data import Player
from response.data import Status
from response.player_response_handler import PlayerResponse


class PlayersResponse:
    def __init__(self, player_reponse: PlayerResponse):
        self.player_response = player_reponse

    def to_response(self, players: list[Player]) -> tuple[Status, dict]:
        return (
            Status(200),
            {  # type: ignore
                "data": [
                    self.player_response.to_player_response(player)
                    for player in players
                ],
                "links": {"self": f"{self.player_response.base_url}/api/players"},
                "meta": {
                    "page": 1,
                    "previous": None,
                    "next": None,
                    "count": len(players),
                },
            },
        )
