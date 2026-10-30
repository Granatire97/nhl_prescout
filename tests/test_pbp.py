from pipeline.ingestion.pbp import has_plays

def test_check_plays():
    plays_exist = {
        "plays": [
            {
                "eventId": 52,
                "periodDescriptor": {
                    "number": 1,
                    "periodType": "REG",
                    "maxRegulationPeriods": 3
                },
                "timeInPeriod": "00:00",
                "timeRemaining": "20:00",
                "situationCode": "1551",
                "homeTeamDefendingSide": "right",
                "typeCode": 520,
                "typeDescKey": "period-start",
                "sortOrder": 8
            },
            {
                "eventId": 51,
                "periodDescriptor": {
                    "number": 1,
                    "periodType": "REG",
                    "maxRegulationPeriods": 3
                },
                "timeInPeriod": "00:00",
                "timeRemaining": "20:00",
                "situationCode": "1551",
                "homeTeamDefendingSide": "right",
                "typeCode": 502,
                "typeDescKey": "faceoff",
                "sortOrder": 11,
                "details": {
                    "eventOwnerTeamId": 17,
                    "losingPlayerId": 8482665,
                    "winningPlayerId": 8484471,
                    "xCoord": 0,
                    "yCoord": 0,
                    "zoneCode": "N"
                }
            }
        ]
    }
    no_plays = {"plays": []}
    empty_dict = {}

    assert not has_plays(plays_exist)
    assert has_plays(no_plays) == ["EMPTY_PLAYS"]
    assert has_plays(empty_dict)  == ["EMPTY_PLAYS"]