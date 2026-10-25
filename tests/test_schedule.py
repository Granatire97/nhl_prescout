from pipeline.ingestion.schedule import filter_schedule
fake_game_schedule = {
    "currentSeason": 20262027,
    "games": [
        {
            "id": 1,
            "season": 20262027,
            "gameType": 1,
            "gameDate": "2026-09-21",
            "gameState": "FINAL",
            "awayTeam": {
                "id": 1,
                "commonName": {
                    "default": "Red Wings"
                },
                "placeName": {
                    "default": "Detroit"
                },
                "placeNameWithPreposition": {
                    "default": "Detroit",
                    "fr": "de Detroit"
                },
                "abbrev": "DET",
                "score": 0
            },
            "homeTeam": {
                "id": 2,
                "commonName": {
                    "default": "Blue Jackets"
                },
                "placeName": {
                    "default": "Columbus"
                },
                "placeNameWithPreposition": {
                    "default": "Columbus",
                    "fr": "de Columbus"
                },
                "abbrev": "CBJ",
                "score": 1
            }
        },
        {
            "id": 2,
            "season": 20262027,
            "gameType": 2,
            "gameDate": "2026-10-18",
            "gameState": "OFF",
            "awayTeam": {
                "id": 1,
                "commonName": {
                    "default": "Red Wings"
                },
                "placeName": {
                    "default": "Detroit"
                },
                "placeNameWithPreposition": {
                    "default": "Detroit",
                    "fr": "de Detroit"
                },
                "abbrev": "DET",
                "score": 2
            },
            "homeTeam": {
                "id": 3,
                "commonName": {
                    "default": "Penguins"
                },
                "placeName": {
                    "default": "Pittsburgh"
                },
                "placeNameWithPreposition": {
                    "default": "Pittsburgh",
                    "fr": "de Pittsburgh"
                },
                "abbrev": "PIT",
                "score": 3
            }
        },
        {
            "id": 3,
            "season": 20262027,
            "gameType": 2,
            "gameDate": "2026-10-21",
            "gameState": "OFF",
            "homeTeam": {
                "id": 1,
                "commonName": {
                    "default": "Red Wings"
                },
                "placeName": {
                    "default": "Detroit"
                },
                "placeNameWithPreposition": {
                    "default": "Detroit",
                    "fr": "de Detroit"
                },
                "abbrev": "DET",
                "score": 5
            },
            "awayTeam": {
                "id": 4,
                "commonName": {
                    "default": "Flames"
                },
                "placeName": {
                    "default": "Calgary"
                },
                "placeNameWithPreposition": {
                    "default": "Calgary",
                    "fr": "de Calgary"
                },
                "abbrev": "CGY",
                "score": 1
            }
        },
        {
            "id": 4,
            "season": 20262027,
            "gameType": 2,
            "gameDate": "2026-11-21",
            "gameState": "FUT",
            "homeTeam": {
                "id": 1,
                "commonName": {
                    "default": "Red Wings"
                },
                "placeName": {
                    "default": "Detroit"
                },
                "placeNameWithPreposition": {
                    "default": "Detroit",
                    "fr": "de Detroit"
                },
                "abbrev": "DET",
            },
            "awayTeam": {
                "id": 5,
                "commonName": {
                    "default": "Blackhawks"
                },
                "placeName": {
                    "default": "Chicago"
                },
                "placeNameWithPreposition": {
                    "default": "Chicago",
                    "fr": "de Chicago"
                },
                "abbrev": "CHI"
            }
        }
    ]
}
fake_game_schedule_empty = {
    "currentSeason": 20272028,
    "games": []
}


def test_only_completed_reg_season():
    results = filter_schedule(fake_game_schedule, "DET")
    assert [item.get("game_id") for item in results] == [2, 3]

def test_is_home_flag():
    results = filter_schedule(fake_game_schedule, "DET")
    flags = {item["game_id"]: item["is_home"] for item in results}
    assert flags == {2: False, 3: True}

def test_empty_schedule():
    assert filter_schedule(fake_game_schedule_empty, "DET") == []