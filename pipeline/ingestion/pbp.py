import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL, PBP_ENDPOINT
from pipeline.ingestion.schedule import raw_schedule, filter_schedule
from pipeline.storage import write_json_atomic

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    setting = yaml.safe_load(file)

team = setting["team"]
season = setting["season"]

class PbpConfig(dg.Config):
    force: bool = False

@dg.asset(deps=[raw_schedule])
async def raw_pbp(context: dg.AssetExecutionContext, config: PbpConfig):
    """ Gets all completed play by play"""
    season_path = RAW_DIR / str(season)
    schedule_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    with open(schedule_path, "r", encoding="utf-8") as file:
        schedule = json.load(file)

    completed_games = filter_schedule(schedule, team)
    if not completed_games:
        raise ValueError(f"No completed regular season games for {team} in {season}, nothing to fetch.")

    game_ids = [game["game_id"] for game in completed_games]

    if config.force:
        games_to_fetch, skipped_games = game_ids, []
    else: 
        games_to_fetch, skipped_games = skip_games(game_ids, season_path)

    failed_games = []
    flagged_games = []
    if not games_to_fetch:
        return dg.MaterializeResult(
        metadata={
            "games_attempted": len(completed_games), 
            "games_downloaded": 0,
            "season": season,
            "games_skipped": len(skipped_games),
            "games_failed": len(failed_games),
            "failed_game_ids": [game_id for game_id, _ in failed_games],
            "games_flagged": len(flagged_games),
            "flagged_game_ids": flagged_games
        }
    )
    url_list = [BASE_URL + PBP_ENDPOINT.format(game_id=game_id) for game_id in games_to_fetch]

    pbp_data = (await fetch_many(url_list, return_exceptions=True))
    context.log.info("Fetch all completed pbp")
    
    for game_id, result in zip(games_to_fetch, pbp_data):

        if isinstance(result, Exception):
            failed_games.append((game_id, str(result)))
            context.log.warning(f"Failed to process game {game_id}: {result}")
            continue

        out_path = RAW_DIR / str(season) / str(game_id) / "pbp.json"
        write_json_atomic(out_path, result)

        if not has_plays(result):
            flagged_games.append(game_id)
            context.log.warning(f"{game_id} has been flagged due to no plays")
        
    context.log.info(f"Attempted: {len(completed_games)}, downloaded: {len(pbp_data) - len(failed_games)}, skipped: {len(skipped_games)}, failed: {len(failed_games)}, flagged: {len(flagged_games)}")
    return dg.MaterializeResult(
        metadata={
            "games_attempted": len(completed_games), 
            "games_downloaded": len(pbp_data) - len(failed_games),
            "season": season,
            "games_skipped": len(skipped_games),
            "games_failed": len(failed_games),
            "failed_game_ids": [game_id for game_id, _ in failed_games],
            "games_flagged": len(flagged_games),
            "flagged_game_ids": flagged_games
        }
    )

def skip_games(game_ids, season_path):
    to_fetch = [game_id for game_id in game_ids if not (season_path / str(game_id) / "pbp.json").exists()]
    skipped = [game_id for game_id in game_ids if (season_path / str(game_id) / "pbp.json").exists()]
    return to_fetch, skipped

def has_plays(pbp):
    return bool(pbp.get("plays"))