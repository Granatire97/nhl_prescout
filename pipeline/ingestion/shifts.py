import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.endpoints import SHIFTCHART_ENDPOINT, BASE_REST_URL
from pipeline.ingestion.schedule import load_completed_game_ids
from pipeline.ingestion.boxscore import raw_boxscore
from pipeline.ingestion.cache import cache_games

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"
MIN_PLAYERS_PER_TEAM = 18
MIN_REG_END_SECONDS = 19 * 60

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    setting = yaml.safe_load(file)

team = setting["team"]
season = setting["season"]

class ShiftsConfig(dg.Config):
    force: bool = False

@dg.asset(deps=[raw_boxscore])
async def raw_shifts(context: dg.AssetExecutionContext, config: ShiftsConfig):
    """ Gets all completed shifts"""

    game_ids = load_completed_game_ids()

    return await cache_games(context=context, game_ids=game_ids, season=season, endpoint=SHIFTCHART_ENDPOINT, filename="shifts.json", validate=check_shifts, force=config.force, base_url=BASE_REST_URL)

def mmss_to_seconds(time_str):
    parts = list(map(int, time_str.split(':')))
    return parts[0] * 60 + parts[1]

def check_shifts(shifts):
    # get the player shift card dicts
    playerShiftCard = shifts.get("data", [])
    shift_rows = [r for r in playerShiftCard if r.get("typeCode") == 517]

    # filter the rows to only look at 517 for non empty shifts
    if not shift_rows:
        return ["EMPTY_SHIFTS"]
    
    flags = []
    team_to_players = {}

    for row in shift_rows:
        team_to_players.setdefault(row["teamId"], set()).add(row["playerId"])
    
    if len(team_to_players) < 2:
        flags.append("PARTIAL_SHIFTS")
    elif any(len(player_set) < MIN_PLAYERS_PER_TEAM for player_set in team_to_players.values()):
        flags.append("PARTIAL_SHIFTS")
    
    # get the game id of the first dict
    game_id = shift_rows[0].get("gameId")

    # read the boxscore for the game id
    game_boxscore_path = RAW_DIR / str(season) / str(game_id) / "boxscore.json"
    with open(game_boxscore_path, "r", encoding="utf-8") as file:
        boxscore = json.load(file)

    # variables set for later on use
    games_final_period = boxscore.get("periodDescriptor")["number"]
    period_type = boxscore.get("periodDescriptor")["periodType"]
    if period_type == "SO":
        expected_last_shift_period = games_final_period - 1
    else: 
        expected_last_shift_period = games_final_period

    max_period = max(item["period"] for item in shift_rows)
        
    # check if the max period is different from the final boxscore period
    if max_period < expected_last_shift_period:
        flags.append("TRUNCATED_SHIFTS")

    elif games_final_period == 3:
        last_end = max(mmss_to_seconds(r["endTime"]) for r in shift_rows if r["period"] == 3)
        if last_end < MIN_REG_END_SECONDS:
            flags.append("TRUNCATED_SHIFTS")
    return flags
