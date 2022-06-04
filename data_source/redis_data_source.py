import json
from dataclasses import asdict
from typing import Optional

from data_source.data_source import DataSource
from redis import Redis

from data_source.json_encoder import GameStateEncoder
from gamestate.data import (
    GameState,
    Player,
    GamePlayers,
    GameBoard,
    Move,
    XO,
    GameResult,
)


class RedisDataSource(DataSource):
    PLAYERS_PREFIX = "players"
    GAMES_PREFIX = "games"

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def add_player(self, player: Player) -> None:
        self.redis_client.set(
            f"{self.PLAYERS_PREFIX}.{player.id}", json.dumps(asdict(player))
        )

    def get_player(self, player_id: str) -> Optional[Player]:
        maybe_player = self.redis_client.get(f"{self.PLAYERS_PREFIX}.{player_id}")
        if maybe_player is None:
            return None
        return Player(**json.loads(maybe_player))

    def get_player_games(self, player_id: str) -> list[GameState]:
        all_games = self.get_games()
        return [
            game
            for game in all_games
            if (game.players.player_x and game.players.player_x.id == player_id)
            or (game.players.player_o and game.players.player_o == player_id)
        ]

    def get_players(self) -> list[Player]:
        all_player_keys = self.redis_client.keys(f"{self.PLAYERS_PREFIX}.*")
        all_players = self.redis_client.mget(all_player_keys)
        return [Player(**json.loads(player)) for player in all_players]  # type: ignore

    def get_games(self) -> list[GameState]:
        all_game_keys = self.redis_client.keys(f"{self.GAMES_PREFIX}.*")
        all_games = self.redis_client.mget(all_game_keys)
        return [self._parse_game_dict(json.loads(game)) for game in all_games]  # type: ignore

    def get_game(self, game_id: str) -> Optional[GameState]:
        if game_dict := self.redis_client.get(f"{self.GAMES_PREFIX}.{game_id}"):
            return self._parse_game_dict(json.loads(game_dict))
        return None

    def update_game(self, game: GameState) -> None:
        self.redis_client.set(
            f"{self.GAMES_PREFIX}.{game.id}",
            json.dumps(asdict(game), cls=GameStateEncoder),
        )

    @staticmethod
    def _players_from_dict(game_dict: dict) -> GamePlayers:
        player_x = game_dict["players"]["player_x"]
        player_o = game_dict["players"]["player_o"]
        return GamePlayers(
            player_x=None if not player_x else Player(**player_x),
            player_o=None if not player_o else Player(**player_o),
        )

    @staticmethod
    def _gameboard_from_dict(game_dict: dict) -> GameBoard:
        x_or_o_board = []
        for row in game_dict["board"]["board"]:
            x_or_o_row: list[Optional[XO]] = []
            for col in row:
                if col is None:
                    x_or_o_row.append(col)
                else:
                    x_or_o_row.append(XO(col))
            x_or_o_board.append(x_or_o_row)
        return GameBoard(board=x_or_o_board)

    @classmethod
    def _parse_game_dict(cls, game_dict: dict) -> GameState:
        return GameState(
            id=game_dict["id"],
            players=cls._players_from_dict(game_dict),
            board=cls._gameboard_from_dict(game_dict),
            next_move=XO(game_dict["next_move"]),
            newest_move=None
            if not game_dict["newest_move"]
            else Move(
                token=XO(game_dict["newest_move"]["token"]),
                position=game_dict["newest_move"]["position"],
            ),
            game_result=GameResult(game_dict["game_result"]),
        )
