# Tic Tac Toe REST API

## To Run:
from the root of the project directory run:
```bash
docker-compose up
```

## A Note about the API request/response structures:
The [json-api-spec](https://jsonapi.org) was generally followed in order to provide
clear structure to the objects that are being represented in the url, request and response bodies.

# To Play:

## Register a new Player 
NOTE: by default, the baseurl for the app will be:
`localhost:8000`

Send a `POST` request to `{{baseUrl}}/api/players`
```
curl --location --request POST 'http://localhost:8000/api/players' \
--header 'Content-Type: application/json' \
--data-raw '{
    "data": {
        "type": "players",
        "attributes": {
            "name": "YourName"
        }
    }
}'
```

Expected response will be something like:
```json
{
    "data": {
        "id": "eebf33",
        "type": "players",
        "attributes": {
            "name": "YourName"
        }
    },
    "links": {
        "self": "http://localhost:8000/api/players/eebf33"
    }
}
```
Retrieve the user id from `data.id` (`"eebf33"` in this case) in the 201 response.
You'll need to pass it as a `User-Id` to create and participate in games.


### Create a new Tic Tac Toe Game
Send a `POST` request to `{{baseUrl}}/api/games`, passing `User-Id`:
```bash
curl --location --request POST 'http://localhost:8000/api/games/' \
--header 'User-Id: eebf33' \
--header 'Content-Type: application/json' \
--data-raw '{
    "data": {
        "type": "games"
    }
}'

```

Expected response will be:
```json

{
    "data": {
        "id": "572f58",
        "type": "games",
        "attributes": {
            "board": [
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ]
            ],
            "next_move": 1,
            "newest_move": null,
            "game_result": "pending"
        },
        "relationships": {
            "player_x": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            },
            "player_o": null
        }
    },
    "links": {
        "self": "http://localhost:8000/api/games/572f58"
    }
}
```
### Some Notes on the Initial Game object
`data.id`: This is the **game_id**. You will need this for subsequently viewing and updating the current game.

`data.attributes.board`: This is the heart of the game! Every space is initialized as `null`. In subsequent updates,
(after `player_o` joins), `player_x` will attempt to get three x's in a row(represented as `1`s on the board)
and `player_o` will attempt to get three o's (represented as `0`s on the board)

`data.attributes.next_move`: Initialized as `1`, denoting that it's `player_x`'s turn first. 
After `player_x` makes a move, it will switch to `0`. Attempts to update out of turn, will result in an error.

`data.attributes.newest_move`: Initialized as `null`. This is the value players update to make moves. 
More on this to follow.

`data.attributes.game_result`: Initialized as `pending`.
Possible other values after subequent updates are `o_wins`, `x_wins`, `draw`
Once the `game_result` is no longer `pending`, the game is over and no additional updates are possible.

`data.relationships.player_x.data.id` Automatically populated with the game creator's user-id. You're player x!

`data.relationships.player_o`: Initialized as `null` That means the game needs updated to add another player.

## Update the Game: Have Player O Join
Before a game can be played, you need another player. For the example, you'll just play yourself. If you play against someone else,
they also will first have to register via `POST` to `/api/players/`

Send a `PATCH` request to `{{baseUrl}}/api/games/{{game_id}}`
```bash
curl --location --request PATCH 'http://localhost:8000/api/games/572f58' \
--header 'User-Id: eebf33' \
--header 'Content-Type: application/json' \
--data-raw '{
    "data": {
        "type": "games",
        "id": "572f58",
        "relationships" : {
            "player_o": {
              "data": {
                "type": "players",
                "id": "eebf33"
              }
            }
        }
    }
}'
```
Expected response:
```json
{
    "data": {
        "id": "572f58",
        "type": "games",
        "attributes": {
            "board": [
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ]
            ],
            "next_move": 1,
            "newest_move": null,
            "game_result": "pending"
        },
        "relationships": {
            "player_x": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            },
            "player_o": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            }
        }
    },
    "links": {
        "self": "http://localhost:8000/api/games/572f58"
    }
}
```
### Notes:
`data.relations.player_o.data.id`: Is now set to the second player's user id (which happens to also be you). 
You're ready to play!

## Update the Game: X Moves
### Valid Moves:
Moves are made by updating the `newest_move` object. The only valid schema for this object is:
`{"token": int, "postion": [int, int] }`
The `token` value must be `1` or `0` representing `X` and `O`, respectively.
And the value passed must match the previous response's `next_move` value.

The `position` value must be a two element array of numbers (`ns`) whose values are such that: `0 <= n < 3`
(The token has to fit within the 3 X 3 board.)
The position has the additional constraint that it can't point to a point that is not `null`

```bash
curl --location --request PATCH 'http://localhost:8000/api/games/572f58' \
--header 'User-Id: eebf33' \
--header 'Content-Type: application/json' \
--data-raw '{
    "data": {
        "type": "games",
        "id": "572f58",
        "attributes": {
            "newest_move": {
                "token": 1,
                "position": [0,2]
            }
        }
    }
}'
```

Expected response:
```json
{
    "data": {
        "id": "572f58",
        "type": "games",
        "attributes": {
            "board": [
                [
                    null,
                    null,
                    1
                ],
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ]
            ],
            "next_move": 0,
            "newest_move": {
                "token": 1,
                "position": [
                    0,
                    2
                ]
            },
            "game_result": "pending"
        },
        "relationships": {
            "player_x": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            },
            "player_o": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            }
        }
    },
    "links": {
        "self": "http://localhost:8000/api/games/572f58"
    }
}
```

### Notes on the response
`data.attributes.board`: The board now has the position [0, 2] populated with `1` or X
`data.attributes.newest_move`: Shows that last valid move
`data.attributes.next_move`: Is now `0`. Meaning that next `newest_move` update must be for `player_o`


## Continue updating the game with `newest_move` updates: 
One more example for Player O:
```bash
curl --location --request GET 'http://localhost:8000/api/games/572f58' \
--header 'User-Id: eebf33' \
--header 'Content-Type: application/json' \
--data-raw '{
    "data": {
        "type": "games",
        "id": "572f58",
        "attributes": {
            "newest_move": {
                "token": 0,
                "position": [0,1]
            }
        }
    }
}'
```


Response:
```json
{
    "data": {
        "id": "572f58",
        "type": "games",
        "attributes": {
            "board": [
                [
                    null,
                    0,
                    1
                ],
                [
                    null,
                    null,
                    null
                ],
                [
                    null,
                    null,
                    null
                ]
            ],
            "next_move": 1,
            "newest_move": {
                "token": 0,
                "position": [
                    0,
                    1
                ]
            },
            "game_result": "pending"
        },
        "relationships": {
            "player_x": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            },
            "player_o": {
                "data": {
                    "type": "players",
                    "id": "eebf33"
                },
                "links": {
                    "self": "http://localhost:8000/api/players/eebf33"
                }
            }
        }
    },
    "links": {
        "self": "http://localhost:8000/api/games/572f58"
    }
}
```

x and o continue taking turns till the response has `data.attributes.game_result` as: `o_wins`, `x_wins`, or `draw`


### If you make an request mistake and you lose track of your board:
 Make a `GET` to `/api/games/{{game_id}}`
To get your last known state for this specific game

OR To view all *your* active games: Make a `GET` to `/api/players/{player_id}/games`

OR to view ALL games: Make a `GET` to `/api/games`




To view your player profile: Make a `GET` to `api/players/{player_id}`

To view all players Make a `GET` to `api/players/`

