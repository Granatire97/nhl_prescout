import dagster as dg
import yaml
from pathlib import Path
from pipeline.client import fetch_many
from pipeline.endpoints import BASE_URL, SCHEDULE_ENDPOINT
from pipeline.storage import write_json_atomic

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
async def raw_schedule(context: dg.AssetExecutionContext):
    """ Gets full raw schedule"""
    try: 
        team_data = (await fetch_many([SCHEDULE_URL]))[0]
        context.log.info(f"Successfully fetched {team} schedule for season {season}.")
    except ValueError as e:
        raise ValueError(f"No schedule found for team '{team}' in season {season}. Check team and season in {CONFIG_PATH}.") from e 
    
    if not team_data.get("games"):
        raise ValueError(f"No games found for team '{team}' in season {season}. Check the season in {CONFIG_PATH}.")
    
    out_path = RAW_DIR / str(season) / f"schedule_{team}.json"
    write_json_atomic(out_path, team_data)

    completed_games = filter_schedule(team_data, team)

    if len(completed_games) == 0:
        context.log.warning(f"0 completed regular season games for {team} in {season}.")

    return dg.MaterializeResult(
        metadata={
            "season": season,
            "team": team,
            "file_size_bytes": out_path.stat().st_size,
            "path": str(out_path),
            "completed_regular_season_games": len(completed_games)
        }
    )

def filter_schedule(schedule, team):
    completed_game_list = []
    for game in schedule.get("games", []):
        awayTeam = game.get("awayTeam", {})
        homeTeam = game.get("homeTeam", {}) 

        if game.get("gameType") == 2 and (game.get("gameState") in ("OFF", "FINAL")):
            game_record = {
                "game_id": game.get("id"),
                "date": game.get("gameDate"),
                "away_team": awayTeam.get("abbrev"),
                "home_team": homeTeam.get("abbrev"),
                "is_home": homeTeam.get("abbrev") == team
            }
            completed_game_list.append(game_record)
    return completed_game_list