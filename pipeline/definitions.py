from dagster import Definitions, load_assets_from_modules
from pipeline.ingestion import schedule, pbp, boxscore, shifts

all_assets = load_assets_from_modules([schedule, pbp, boxscore, shifts])

defs = Definitions(
    assets = all_assets,
)