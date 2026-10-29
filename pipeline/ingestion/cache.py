import dagster as dg
from pathlib import Path
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL
from pipeline.storage import write_json_atomic

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"

async def cache_games(context, game_ids, season, endpoint, filename, validate, force):
    """ Gets all completed results"""
    season_path = RAW_DIR / str(season)

    if force:
        games_to_fetch, skipped_games = game_ids, []
    else: 
        games_to_fetch, skipped_games = skip_games(game_ids, season_path, filename)

    failed_games = []
    flagged_games = []
    if not games_to_fetch:
        context.log.warning(f"Attempted: {len(game_ids)}, Downloaded: 0, Skipped: {len(skipped_games)}, Failed: {len(failed_games)}, Flagged: {len(flagged_games)}")
        return dg.MaterializeResult(
        metadata={
            "games_attempted": len(game_ids), 
            "games_downloaded": 0,
            "season": season,
            "games_skipped": len(skipped_games),
            "games_failed": len(failed_games),
            "failed_game_ids": [game_id for game_id, _ in failed_games],
            "games_flagged": len(flagged_games),
            "flagged_game_ids": flagged_games
        }
    )
    url_list = [BASE_URL + endpoint.format(game_id=game_id) for game_id in games_to_fetch]

    results = (await fetch_many(url_list, return_exceptions=True))
    context.log.info(f"Fetched {len(games_to_fetch)} {filename} files")
    
    for game_id, result in zip(games_to_fetch, results):

        if isinstance(result, Exception):
            failed_games.append((game_id, str(result)))
            context.log.warning(f"Failed to process game {game_id}: {result}")
            continue

        out_path = RAW_DIR / str(season) / str(game_id) / filename
        write_json_atomic(out_path, result)

        if not validate(result):
            flagged_games.append(game_id)
            context.log.info(f"{game_id} flagged: {filename} failed validation")
        
    context.log.info(f"Attempted: {len(game_ids)}, Downloaded: {len(results) - len(failed_games)}, Skipped: {len(skipped_games)}, Failed: {len(failed_games)}, Flagged: {len(flagged_games)}")
    return dg.MaterializeResult(
        metadata={
            "games_attempted": len(game_ids), 
            "games_downloaded": len(results) - len(failed_games),
            "season": season,
            "games_skipped": len(skipped_games),
            "games_failed": len(failed_games),
            "failed_game_ids": [game_id for game_id, _ in failed_games],
            "games_flagged": len(flagged_games),
            "flagged_game_ids": flagged_games
        }
    )

def skip_games(game_ids, season_path, filename):
    to_fetch = [game_id for game_id in game_ids if not (season_path / str(game_id) / filename).exists()]
    skipped = [game_id for game_id in game_ids if (season_path / str(game_id) / filename).exists()]
    return to_fetch, skipped