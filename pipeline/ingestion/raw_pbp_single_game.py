import dagster as dg
import httpx
import yaml
import aiohttp
import asyncio
from tqdm.asyncio import tqdm_asyncio
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    config = yaml.safe_load(file)

team = config["team"]
season = config["season"]
SCHEDULE_URL = "https://api-web.nhle.com/v1/club-schedule-season/{}/{}"

# First asset - Full DETROIT RED WINGS schedule
@dg.asset
async def get_raw_redwings_schedule(context: dg.AssetExecutionContext):
    """ Gets full red wings schedule"""
    async def fetch_team_schedule(session, team, season, sem, retries=3):
        url = SCHEDULE_URL.format(team, season)
        async with sem:  # throttle concurrency
            for attempt in range(retries):
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        elif resp.status == 404:
                            raise ValueError(f"Schedule not found for {team} {season}")
                        else:
                            raise RuntimeError(f"Schedule request failed: HTTP {resp.status}")
                except ValueError:
                    raise
                except Exception as e:
                    if attempt == retries - 1:
                        raise RuntimeError(f"Schedule fetch failed after {retries} tries") from e
                    await asyncio.sleep(0.5)

    async def fetch_all_games(concurrency=10):
        sem = asyncio.Semaphore(concurrency)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [
                fetch_team_schedule(session, team, season, sem)
            ]
            results = await tqdm_asyncio.gather(*tasks)
            return results
        
    team_data = await fetch_all_games()
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
def raw_pbp_single_game(context: dg.AssetExecutionContext):
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
    # Use a synchronous client context manager
    with httpx.Client() as client:
        response = client.get(f"https://api-web.nhle.com/v1/gamecenter/{one_game}/play-by-play")
        context.log.info("Fetch a single pbp for one game")

        if response.status_code == 200:
            single_pbp_data = response.json()

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
        else:
            raise Exception("Failed to fetch pbp for this game")


