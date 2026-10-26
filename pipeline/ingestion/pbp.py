import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL, PBP_ENDPOINT
from pipeline.ingestion.schedule import raw_schedule, filter_schedule

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    config = yaml.safe_load(file)

team = config["team"]
season = config["season"]

@dg.asset(deps=[raw_schedule])
async def raw_pbp(context: dg.AssetExecutionContext):
    """ Gets all completed play by play"""
    schedule_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    with open(schedule_path, "r", encoding="utf-8") as file:
        schedule = json.load(file)

    completed_games = filter_schedule(schedule, team)
    if not completed_games:
        raise ValueError(f"No completed regular season games for {team} in {season}, nothing to fetch.")

    game_ids = [game["game_id"] for game in completed_games]
    url_list = [BASE_URL + PBP_ENDPOINT.format(game_id=game_id) for game_id in game_ids]

    pbp_data = (await fetch_many(url_list))
    context.log.info("Fetch all completed pbp")
    for game in pbp_data:
            
        out_path = RAW_DIR / str(season) / str(game["id"]) / "pbp.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as file:
            json.dump(game, file, indent=4)
        
    return dg.MaterializeResult(
        metadata={
            "games_downloaded": len(pbp_data),
            "season": season
        }
    )