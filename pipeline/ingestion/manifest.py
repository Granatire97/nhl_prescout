import dagster as dg
import yaml
import json
from pathlib import Path
from pipeline.ingestion.pbp import raw_pbp
from pipeline.ingestion.boxscore import raw_boxscore
from pipeline.ingestion.shifts import raw_shifts
from pipeline.setup_warehouse import create_warehouse
import duckdb
from pipeline.endpoints import DB_PATH

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "settings.yaml"
MANIFEST_DIR = ROOT / "data" / "manifest"

# Open the YAML file and load its contents
with open(CONFIG_PATH, "r") as file:
    # safe_load prevents execution of arbitrary code embedded in YAML files
    config = yaml.safe_load(file)

team = config["team"]
season = config["season"]

# Manifest Asset
@dg.asset(deps=[raw_shifts, raw_boxscore, raw_pbp])
def ingest_manifest(context: dg.AssetExecutionContext) -> None:
        """Function that will be called to load the updated manifest table """
        create_warehouse()
        manifest_glob_path = MANIFEST_DIR / "*.jsonl"
        con = duckdb.connect(DB_PATH)
        try:
            con.execute("""
                        CREATE OR REPLACE TABLE ingest.manifest_latest AS
                        SELECT *
                        FROM read_json_auto(?, union_by_name = true)
                        WHERE season = ?
                        QUALIFY ROW_NUMBER() OVER (PARTITION BY season, game_id, endpoint ORDER BY run_ts DESC) = 1
                        """, [str(manifest_glob_path), season])
            con.execute("""
                        CREATE OR REPLACE TABLE ingest.manifest_games AS
                        SELECT 
                            game_id, 
                            season, 
                            CASE
                                WHEN COUNT(*) = 3
                                AND COUNT(*) FILTER (WHERE status = 'FAILED') = 0
                                AND COUNT(*) FILTER (WHERE len(flags) > 0) = 0
                                THEN 1 ELSE 0
                            END AS usable,
                            LIST(flags) AS all_flags
                        FROM ingest.manifest_latest
                        GROUP BY season, game_id
                        """)
        finally:
             con.close()

