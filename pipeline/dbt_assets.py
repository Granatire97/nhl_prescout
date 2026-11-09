
from pathlib import Path

import dagster as dg
from dagster_dbt import DbtProject, DbtCliResource, dbt_assets

ROOT = Path(__file__).resolve().parents[1]

# Configure dbt project
dbt_project = DbtProject(
    project_dir=ROOT / "analytics",
    profiles_dir=ROOT / "analytics",
)

# Prepare dbt manifest during development
dbt_project.prepare_if_dev()


# Register dbt models as Dagster assets
@dbt_assets(manifest=dbt_project.manifest_path)
def nhl_prescout_dbt_assets(
    context: dg.AssetExecutionContext,
    dbt: DbtCliResource,
):
    yield from dbt.cli(
        ["build"],
        context=context,
    ).stream()
