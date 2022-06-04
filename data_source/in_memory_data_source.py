from dataclasses import asdict
from typing import Optional

from data_source.data_source import DataSource
from gamestate.data import (
    Player,
    GameState,
    GamePlayers,
    GameBoard,
    Move,
    XO,
    GameResult,
)


class InMemoryDataSource(DataSource):
    def __init__(self, data: dict):
        self.data = data

    def get_player_games(self, player_id: str) -> list[GameState]:
        # TODO: This is a whole "table scan". Not great.
        #  Probably should have a separate set of keys for the relation
        #   or it might make sense to swap for a relational db.
        games = self.get_games()
        return [
            game
            for game in games
            if (game.players.player_o and game.players.player_o.id == player_id)
            or (game.players.player_x and game.players.player_x == player_id)
        ]

    def get_players(self) -> list[Player]:
        return [
            Player(**player_dict)
            for player_dict in self.data.get("players", {}.values())
        ]

    def get_player(self, player_id: str) -> Optional[Player]:
        if player_dict := self.data.get("players", {}).get(player_id, None):
            return Player(**player_dict)
        return None

    def get_games(self) -> list[GameState]:
        return [
            self._parse_game_dict(game) for game in self.data.get("games", {}).values()
        ]

    def get_game(self, game_id: str) -> Optional[GameState]:
        if game_dict := self.data.get("games", {}).get(game_id):
            return self._parse_game_dict(game_dict)
        return None

    def add_player(self, player: Player) -> None:
        self.data["players"][player.id] = asdict(player)

    def update_game(self, game: GameState) -> None:
        self.data["games"][game.id] = asdict(game)

    @staticmethod
    def _players_from_dict(game_dict: dict) -> GamePlayers:
        player_x = game_dict["players"]["player_x"]
        player_o = game_dict["players"]["player_o"]
        return GamePlayers(
            player_x=None if not player_x else Player(**player_x),
            player_o=None if not player_o else Player(**player_o),
        )

    @classmethod
    def _parse_game_dict(cls, game_dict: dict) -> GameState:
        return GameState(
            id=game_dict["id"],
            players=cls._players_from_dict(game_dict),
            board=GameBoard(**game_dict["board"]),
            next_move=game_dict["next_move"],
            newest_move=None
            if not game_dict["newest_move"]
            else Move(**game_dict["newest_move"]),
            game_result=game_dict["game_result"],
        )


in_memory_data_source = InMemoryDataSource(
    data={
        "games": {
            "abcd": {
                "id": "abcd",
                "players": {
                    "player_x": {"name": "Joe", "id": "abc"},
                    "player_o": {"name": "Alice", "id": "def"},
                },
                "board": {
                    "board": [
                        [None, None, None],
                        [None, None, None],
                        [None, None, None],
                    ]
                },
                "next_move": XO.X,
                "newest_move": dict(token=XO.X, position=(0, 0)),
                "game_result": GameResult.Pending,
            },
            "ghijkl": {
                "id": "ghijkl",
                "players": {
                    "player_x": {"name": "Joe", "id": "abc"},
                    "player_o": {"name": "Alice", "id": "def"},
                },
                "board": {
                    "board": [
                        [XO.X, None, None],
                        [None, None, None],
                        [None, None, None],
                    ]
                },
                "next_move": XO.O,
                "newest_move": dict(token=XO.X, position=(0, 0)),
                "game_result": GameResult.Pending,
            },
            "zyx": {
                "id": "zyx",
                "players": {
                    "player_x": {"name": "Joe", "id": "abc"},
                    "player_o": None,
                },
                "board": {
                    "board": [
                        [None, None, None],
                        [None, None, None],
                        [None, None, None],
                    ]
                },
                "next_move": XO.O,
                "newest_move": dict(token=XO.X, position=(0, 0)),
                "game_result": GameResult.Pending,
            },
            "finished_game": {
                "id": "finished_game",
                "players": {
                    "player_x": {"name": "Joe", "id": "abc"},
                    "player_o": None,
                },
                "board": {
                    "board": [
                        [XO.O, XO.X, XO.O],
                        [XO.X, XO.O, XO.X],
                        [XO.X, XO.X, XO.O],
                    ]
                },
                "next_move": XO.X,
                "newest_move": dict(token=XO.X, position=(0, 0)),
                "game_result": GameResult.OWins,
            },
        },
        "players": {
            "abc": {"id": "abc", "name": "Joe"},
            "def": {"id": "def", "name": "Alice"},
        },
    }
)
