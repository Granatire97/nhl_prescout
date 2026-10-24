import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL, SCHEDULE_ENDPOINT, PBP_ENDPOINT

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    config = yaml.safe_load(file)

team = config["team"]
season = config["season"]
SCHEDULE_URL = BASE_URL + SCHEDULE_ENDPOINT.format(team=team, season=season)

# First asset - Full DETROIT RED WINGS schedule
@dg.asset
async def get_raw_redwings_schedule(context: dg.AssetExecutionContext):
    """ Gets full red wings schedule"""
    team_data = await fetch_many([SCHEDULE_URL])
    context.log.info(f"Successfully fetched Red Wings schedule for season {season}.")

    out_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(team_data, file, indent=4)

    return dg.MaterializeResult(
        metadata={
            "season": season,
            "team": team,
            "file_size_bytes": out_path.stat().st_size,
            "path": str(out_path)
        }
    )
        
@dg.asset(deps=[get_raw_redwings_schedule])
async def raw_pbp_single_game(context: dg.AssetExecutionContext):
    """ Gets single game play by play for HTTPX Call"""
    schedule_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    with open(schedule_path, "r", encoding="utf-8") as file:
        schedule = json.load(file)

    DET_games = schedule[0].get("games", [])
    # Building game ids list
    game_ids = []
    for game in DET_games:
        for key, value in game.items():
            if key == "id":
                game_ids.append(value)
    
    one_game = game_ids[0]

    PBP_URL = BASE_URL + PBP_ENDPOINT.format(game_id=one_game)
    single_pbp_data = (await fetch_many([PBP_URL]))[0]
    context.log.info("Fetch a single pbp for one game")

    out_path = RAW_DIR / str(season) / str(one_game) / "pbp.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(single_pbp_data, file, indent=4)
        
    return dg.MaterializeResult(
        metadata={
            "game_id": one_game,
            "file_size_bytes": out_path.stat().st_size,
            "path": str(out_path)
        }
    )


