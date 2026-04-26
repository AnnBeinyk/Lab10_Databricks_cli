import os
from dataclasses import dataclass


def get_required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} is not set")
    return value


@dataclass
class Config:
    host: str
    token: str
    email: str
    notebook_path: str
    pipeline_id: str | None = None


def load_config() -> Config:
    return Config(
        host=get_required_env("DATABRICKS_HOST"),
        token=get_required_env("DATABRICKS_TOKEN"),
        email=get_required_env("DATABRICKS_EMAIL"),
        notebook_path=get_required_env("DATABRICKS_NOTEBOOK_PATH"),
        pipeline_id=os.getenv("DATABRICKS_PIPELINE_ID"),
    )

CONFIG = load_config()