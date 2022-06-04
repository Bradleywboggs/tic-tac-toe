from starlette import status

from gamestate.data import Player
from request.data import PlayerError
from response.data import Status


class PlayerResponse:
    error_map: dict = {
        PlayerError.InvalidRequestBody: {
            "pointer": "/data",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        PlayerError.WrongResourceType: {
            "pointer": "/data/type",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        PlayerError.MissingPlayerName: {
            "pointer": "/data/attributes/name",
            "status": Status(status.HTTP_400_BAD_REQUEST),
        },
        PlayerError.PlayerNotFound: {
            "pointer": "/data/id",
            "status": Status(status.HTTP_404_NOT_FOUND),
        },
    }

    def __init__(self, base_url: str):
        self.base_url = base_url

    def to_response(self, response_data: PlayerError | Player) -> dict:
        if isinstance(response_data, PlayerError):
            return (  # type: ignore
                self.error_map[response_data]["status"],
                self.to_error_response(response_data),
            )

        return (Status(status.HTTP_200_OK)), {  # type: ignore
            "data": self.to_player_response(response_data),
            "links": {"self": f"{self.base_url}/api/players/{response_data.id}"},
        }

    def to_player_response(self, player: Player) -> dict:
        return {"id": player.id, "type": "players", "attributes": {"name": player.name}}

    def to_error_response(self, error: PlayerError) -> dict:
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
