import abc
from typing import Optional

from gamestate.data import (
    Player,
    GameState,
)


class DataSource(abc.ABC):
    @abc.abstractmethod
    def get_player(self, player_id: str) -> Optional[Player]:
        pass

    @abc.abstractmethod
    def get_players(self) -> list[Player]:
        pass

    @abc.abstractmethod
    def get_games(self) -> list[GameState]:
        pass

    @abc.abstractmethod
    def get_game(self, game_id: str) -> Optional[GameState]:
        pass

    @abc.abstractmethod
    def get_player_games(self, player_id: str) -> list[GameState]:
        pass

    @abc.abstractmethod
    def add_player(self, player: Player) -> None:
        pass

    @abc.abstractmethod
    def update_game(self, game: GameState) -> None:
        pass
