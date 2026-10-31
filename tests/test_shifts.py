import json
import pipeline.ingestion.shifts as shifts

SEASON = shifts.season
GAME_ID = 1

def make_rows(players_per_team=18, last_period=3, last_end="20:00"):
    rows = []
    for team_id in (1, 2):
        for p in range(players_per_team):
            rows.append({"typeCode": 517, "gameId": GAME_ID, "teamId": team_id,
                         "playerId": team_id * 100 + p, "period": last_period,
                         "endTime": last_end})
    return {"data": rows}

def write_boxscore(tmp_path, number, period_type):
    path = tmp_path / str(SEASON) / str(GAME_ID)
    path.mkdir(parents=True)
    (path / "boxscore.json").write_text(json.dumps(
        {"periodDescriptor": {"number": number, "periodType": period_type}}))
    
def test_partial(tmp_path, monkeypatch):
    monkeypatch.setattr(shifts, "RAW_DIR", tmp_path)
    write_boxscore(tmp_path, 3, "REG")
    assert shifts.check_shifts(make_rows(players_per_team = 15)) == ["PARTIAL_SHIFTS"]

def test_truncated(tmp_path, monkeypatch):
    monkeypatch.setattr(shifts, "RAW_DIR", tmp_path)
    write_boxscore(tmp_path, 3, "REG")
    assert shifts.check_shifts(make_rows(last_end="12:00")) == ["TRUNCATED_SHIFTS"]

def test_shootout(tmp_path, monkeypatch):
    monkeypatch.setattr(shifts, "RAW_DIR", tmp_path)
    write_boxscore(tmp_path, 5, "SO")
    assert shifts.check_shifts(make_rows(last_period=4)) == []

def test_clean(tmp_path, monkeypatch):
    monkeypatch.setattr(shifts, "RAW_DIR", tmp_path)
    write_boxscore(tmp_path, 3, "REG")
    assert shifts.check_shifts(make_rows()) == []
    
def test_empty():
    assert shifts.check_shifts({"data": []}) == ["EMPTY_SHIFTS"]