from dagster import Definitions, load_assets_from_modules
from pipeline.ingestion import raw_pbp_single_game

all_assets = load_assets_from_modules([raw_pbp_single_game])

defs = Definitions(
    assets = all_assets,
)