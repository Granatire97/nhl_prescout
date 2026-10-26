from dagster import Definitions, load_assets_from_modules
from pipeline.ingestion import schedule, pbp

all_assets = load_assets_from_modules([schedule, pbp])

defs = Definitions(
    assets = all_assets,
)