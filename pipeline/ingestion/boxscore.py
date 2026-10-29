import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.endpoints import BOXSCORE_ENDPOINT
from pipeline.ingestion.schedule import raw_schedule, filter_schedule
from pipeline.ingestion.cache import cache_games

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    setting = yaml.safe_load(file)

team = setting["team"]
season = setting["season"]

class BoxscoreConfig(dg.Config):
    force: bool = False

@dg.asset(deps=[raw_schedule])
async def raw_boxscore(context: dg.AssetExecutionContext, config: BoxscoreConfig):
    """ Gets all completed boxscore"""
    schedule_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    with open(schedule_path, "r", encoding="utf-8") as file:
        schedule = json.load(file)

    completed_games = filter_schedule(schedule, team)
    if not completed_games:
        raise ValueError(f"No completed regular season games for {team} in {season}, nothing to fetch.")

    game_ids = [game["game_id"] for game in completed_games]

    return await cache_games(context=context, game_ids=game_ids, season=season, endpoint=BOXSCORE_ENDPOINT, filename="boxscore.json", validate=has_player_stats, force=config.force)

def has_player_stats(boxscore):
    playerByGameStats = boxscore.get("playerByGameStats", {})

    for team_key in ["awayTeam", "homeTeam"]:
        team_data = playerByGameStats.get(team_key, {})
        if not team_data.get("forwards"):
            return False

    return True
    