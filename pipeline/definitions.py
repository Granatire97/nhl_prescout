from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource
from pipeline.ingestion import schedule, pbp, boxscore, shifts, manifest, load_raw
from pipeline.dbt_assets import nhl_prescout_dbt_assets, dbt_project

all_assets = load_assets_from_modules([schedule, pbp, boxscore, shifts, manifest, load_raw])

defs = Definitions(
    assets = [*all_assets, nhl_prescout_dbt_assets],
    resources={"dbt": DbtCliResource(project_dir=dbt_project)}

)