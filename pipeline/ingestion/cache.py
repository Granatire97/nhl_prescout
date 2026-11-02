import dagster as dg
from pathlib import Path
import json
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL
from pipeline.storage import write_json_atomic, append_manifest_rows

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
MANIFEST_DIR = ROOT / "data" / "manifest"

async def cache_games(context, game_ids, season, endpoint, filename, validate, force, base_url=BASE_URL):
    """ Gets all completed results"""
    season_path = RAW_DIR / str(season)
    rows = []
    run_stats = context.instance.get_run_stats(context.run_id)
    run_ts_unix = run_stats.start_time 
    endpoint_name = filename.removesuffix(".json")
    manifest_filename = MANIFEST_DIR / f"{endpoint_name}.jsonl"

    if force:
        games_to_fetch, skipped_games = game_ids, []
    else: 
        games_to_fetch, skipped_games = skip_games(game_ids, season_path, filename)

    for game_id in skipped_games:
        path = season_path / str(game_id) / filename
        with open(path, "r", encoding="utf-8") as file:
            existing = json.load(file)
        rows.append({"run_id":context.run_id, "run_ts":run_ts_unix, "season":season, "game_id": game_id, "endpoint":endpoint_name, "status": "SKIPPED",
                    "file_size_bytes": path.stat().st_size, "flags": validate(existing)})

    failed_games = []
    flagged_games = {}
    if not games_to_fetch:
        context.log.info(f"Attempted: {len(game_ids)}, Downloaded: 0, Skipped: {len(skipped_games)}, Failed: {len(failed_games)}, Flagged: {len(flagged_games)}")
        append_manifest_rows(rows, manifest_filename)
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
    url_list = [base_url + endpoint.format(game_id=game_id) for game_id in games_to_fetch]

    results = (await fetch_many(url_list, return_exceptions=True))
    context.log.info(f"Fetched {len(games_to_fetch)} {filename} files")
    
    for game_id, result in zip(games_to_fetch, results):
        if isinstance(result, Exception):
            failed_games.append((game_id, str(result)))
            context.log.warning(f"Failed to process game {game_id}: {result}")
            rows.append({"run_id":context.run_id, "run_ts":run_ts_unix, "season":season, "game_id":game_id, "endpoint":endpoint_name, "status": "FAILED", "file_size_bytes": None, "flags":[], "error":str(result)})
            continue

        out_path = RAW_DIR / str(season) / str(game_id) / filename
        write_json_atomic(out_path, result)

        flags = validate(result)

        if flags:
            flagged_games[game_id] = flags
            context.log.warning(f"{game_id} flagged: {flags}")
        
        # building rows inside for one row per game
        rows.append({"run_id":context.run_id, "run_ts":run_ts_unix, "season":season, "game_id":game_id, "endpoint":endpoint_name, "status": "DOWNLOADED", "file_size_bytes": out_path.stat().st_size, "flags":flags})
        
    context.log.info(f"Attempted: {len(game_ids)}, Downloaded: {len(results) - len(failed_games)}, Skipped: {len(skipped_games)}, Failed: {len(failed_games)}, Flagged: {len(flagged_games)}")
    context.log.info(f"rows: {rows}")
    append_manifest_rows(rows, manifest_filename)
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