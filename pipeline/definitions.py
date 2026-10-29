from dagster import Definitions, load_assets_from_modules
from pipeline.ingestion import schedule, pbp, boxscore

all_assets = load_assets_from_modules([schedule, pbp, boxscore])

defs = Definitions(
    assets = all_assets,
)