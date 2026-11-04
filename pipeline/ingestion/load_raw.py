import dagster as dg
import yaml
from pathlib import Path
from typing import List, Iterable
from pipeline.ingestion.manifest import ingest_manifest
import duckdb
from pipeline.endpoints import DB_PATH
from pipeline.raw_storage import RAW_PBP, RAW_SHIFTS, RAW_BOXSCORE, RAW_SCHEDULE

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
RAW_DIR = ROOT / "data" / "raw"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    config = yaml.safe_load(file)

team = config["team"]
season = config["season"]

class RawConfig(dg.Config):
    include_unusable: bool = False

# Raw Tables Asset
@dg.asset(deps=[ingest_manifest])
def raw_tables(context: dg.AssetExecutionContext, config:RawConfig) -> dg.MaterializeResult:
    """
    Function that will be called nightly to load all 4 tables
    """
    con = duckdb.connect(DB_PATH)
    query = "SELECT game_id FROM ingest.manifest_games WHERE season = ?"
    if not config.include_unusable:
        query += " AND usable = 1"

    games = [row[0] for row in con.execute(query, [str(season)]).fetchall()]
    pbp_paths = get_existing_paths(season, games, "pbp.json")
    boxscore_paths = get_existing_paths(season, games, "boxscore.json")
    shifts_paths = get_existing_paths(season, games, "shifts.json")
    schedule_path = RAW_DIR / str(season) / f"schedule_{team}.json"


    if not pbp_paths:
        context.log.warning(f"No pbp files to load for season {season}")
        con.close()
        return
    if not boxscore_paths:
        context.log.warning(f"No boxscore files to load for season {season}")
        con.close()
        return
    if not shifts_paths:
        context.log.warning(f"No shifts files to load for season {season}")
        con.close()
        return
    if not schedule_path.exists():
        context.log.warning(f"No schedule to load for season {season} and team {team}")
        con.close()
        return
    
    try:
        # starting transaction 
        con.execute("BEGIN TRANSACTION")
        load_game_table(con, select_sql=RAW_PBP, paths=pbp_paths, temp_table_name="incoming_raw_pbp", table_name="raw.pbp_plays")
        load_game_table(con, select_sql=RAW_BOXSCORE, paths=boxscore_paths, temp_table_name="incoming_raw_boxscore", table_name="raw.boxscore_players")
        load_game_table(con, select_sql=RAW_SHIFTS, paths=shifts_paths, temp_table_name="incoming_raw_shifts", table_name="raw.shifts")
        load_schedule_table(con, select_sql=RAW_SCHEDULE, schedule_path=schedule_path, season=season, team=team, temp_table_name="incoming_raw_schedule", table_name="raw.schedule")

        # per-game row counts
        pbp_query = "SELECT game_id, count(*) FROM raw.pbp_plays GROUP BY game_id ORDER BY game_id"
        boxscore_query = "SELECT game_id, count(*) FROM raw.boxscore_players GROUP BY game_id ORDER BY game_id"
        shifts_query = "SELECT game_id, count(*) FROM raw.shifts GROUP BY game_id ORDER BY game_id"
        pbp_per_game = dict(con.execute(pbp_query).fetchall())
        boxscore_per_game = dict(con.execute(boxscore_query).fetchall())
        shifts_per_game = dict(con.execute(shifts_query).fetchall())

        # log info
        context.log.info(f"pbp rows per game: {pbp_per_game}")
        context.log.info(f"boxscore rows per game: {boxscore_per_game}")
        context.log.info(f"shifts rows per game: {shifts_per_game}")

        # validation query
        validation_query = "SELECT game_id FROM ingest.manifest_games WHERE season = ? AND usable = 1 AND game_id NOT IN (SELECT game_id FROM raw.pbp_plays)"
        validation_query_results = [row[0] for row in con.execute(validation_query, [str(season)]).fetchall()]
        if validation_query_results:
            raise ValueError(f"Missing Game IDs: {validation_query_results}")
        
        # total row counts for each table
        pbp_row_counts = con.execute("SELECT count(*) FROM raw.pbp_plays").fetchone()[0]
        boxscore_row_counts = con.execute("SELECT count(*) FROM raw.boxscore_players").fetchone()[0]
        shifts_row_counts = con.execute("SELECT count(*) FROM raw.shifts").fetchone()[0]

        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    return dg.MaterializeResult(
        metadata={
            "games_loaded": len(games),
            "pbp_row_counts": pbp_row_counts,
            "boxscore_row_counts": boxscore_row_counts,
            "shifts_row_counts": shifts_row_counts,
            "missing_pbp_games": len(validation_query_results)
        }
    )

def load_game_table(con, select_sql, paths, temp_table_name, table_name):
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE {temp_table_name} AS
        {select_sql}
        """, [paths])
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} AS
        SELECT *
        FROM {temp_table_name}
        LIMIT 0
        """)
    con.execute(f"""
                DELETE FROM {table_name}
                WHERE game_id IN (
                    SELECT DISTINCT game_id
                    FROM {temp_table_name})
                """)
    con.execute(f"""
                INSERT INTO {table_name}
                SELECT *
                FROM {temp_table_name}
                """)

def load_schedule_table(con, select_sql, schedule_path, season, team, temp_table_name, table_name):
        con.execute(f"""
            CREATE OR REPLACE TEMP TABLE {temp_table_name} AS
            {select_sql}
            """, [str(schedule_path), team])
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT *
            FROM {temp_table_name}
            LIMIT 0
            """)
        con.execute(f"""
                    DELETE FROM {table_name}
                    WHERE season = ? AND team = ?
                    """, [str(season), str(team)])
        con.execute(f"""
                    INSERT INTO {table_name}
                    SELECT *
                    FROM {temp_table_name}
                    """)
        
def get_existing_paths(season: int, games: Iterable[int], filename: str) -> List[str]:
    paths = []
    for game_id in games:
        path = RAW_DIR / str(season) / str(game_id) / filename
        if path.exists():
            paths.append(str(path))

    return paths
