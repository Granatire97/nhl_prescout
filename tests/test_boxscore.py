from pipeline.ingestion.boxscore import has_player_stats

def test_check_player_stats():
    plays_stats_exist = {
        "playerByGameStats": {
            "awayTeam": {
                "forwards": [
                    {
                    "playerId": 8480009,
                    "sweaterNumber": 17,
                    "name": {
                    "default": "E. Tolvanen"
                    },
                    "position": "R",
                    "goals": 1,
                    "assists": 0,
                    "points": 1,
                    "plusMinus": 1,
                    "pim": 0,
                    "hits": 3,
                    "powerPlayGoals": 0,
                    "sog": 1,
                    "faceoffWinningPctg": 0,
                    "toi": "11:26",
                    "blockedShots": 1,
                    "shifts": 21,
                    "giveaways": 1,
                    "takeaways": 0
                    },
                ]
            },
            "homeTeam": {
                "forwards": [
                    {
                    "playerId": 8477429,
                    "sweaterNumber": 18,
                    "name": {
                    "default": "A. Copp"
                    },
                    "position": "C",
                    "goals": 0,
                    "assists": 0,
                    "points": 0,
                    "plusMinus": -1,
                    "pim": 0,
                    "hits": 1,
                    "powerPlayGoals": 0,
                    "sog": 1,
                    "faceoffWinningPctg": 0.52381,
                    "toi": "22:17",
                    "blockedShots": 1,
                    "shifts": 28,
                    "giveaways": 1,
                    "takeaways": 0
                    }
                ]
            }
        }
    }
    no_player_stats_home = {
        "playerByGameStats": {
            "awayTeam": {
                "forwards": [
                    {
                    "playerId": 8480009,
                    "sweaterNumber": 17,
                    "name": {
                    "default": "E. Tolvanen"
                    },
                    "position": "R",
                    "goals": 1,
                    "assists": 0,
                    "points": 1,
                    "plusMinus": 1,
                    "pim": 0,
                    "hits": 3,
                    "powerPlayGoals": 0,
                    "sog": 1,
                    "faceoffWinningPctg": 0,
                    "toi": "11:26",
                    "blockedShots": 1,
                    "shifts": 21,
                    "giveaways": 1,
                    "takeaways": 0
                    },
                ]
            },
            "homeTeam": {
                "forwards": []
            }
        }
    }
    empty_dict = {}

    assert has_player_stats(plays_stats_exist)
    assert not has_player_stats(no_player_stats_home)
    assert not has_player_stats(empty_dict)
