#!/usr/bin/env python3
"""Generate Evidently AI configuration from Metaflow/Outerbounds credentials.

This script reads the Metaflow config to get PostgreSQL credentials and S3 paths,
then generates an Evidently config YAML file for the service to use.

It follows the same pattern as the Arize Phoenix get_env_vars.py script.
"""

import os
import json
import sys
import yaml


def get_postgres_url():
    """Generate PostgreSQL connection URL using Metaflow credentials.

    On Outerbounds with `persistence: postgres`, a PostgreSQL database is
    available at localhost:5432. The credentials come from the Metaflow config.
    """
    metaflow_home = os.environ.get(
        "METAFLOW_HOME", os.path.expanduser("~/.metaflowconfig")
    )
    config_path = os.path.join(metaflow_home, "config.json")

    try:
        with open(config_path, "r") as f:
            conf = json.load(f)
            token = conf["METAFLOW_SERVICE_AUTH_KEY"]
    except FileNotFoundError:
        print(f"ERROR: Config file not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    except KeyError:
        print("ERROR: METAFLOW_SERVICE_AUTH_KEY not found in config", file=sys.stderr)
        sys.exit(1)

    return f"postgresql://userspace_default:{token}@localhost:5432/userspace_default?sslmode=disable"


def get_s3_workspace_path():
    """Get S3 workspace path from Metaflow config for dataset storage."""
    from metaflow.metaflow_config import DATASTORE_SYSROOT_S3

    prefix = "ob-evidently"
    return os.path.join(DATASTORE_SYSROOT_S3, prefix, "workspace")


def generate_config(output_path="evidently_config.yaml", use_postgres=True):
    """Generate Evidently configuration file.

    Args:
        output_path: Where to write the config file.
        use_postgres: If True, use PostgreSQL + S3. If False, use SQLite (local dev).
    """
    if use_postgres:
        pg_url = get_postgres_url()
        s3_workspace = get_s3_workspace_path()

        config = {
            "storage": {"type": "sql"},
            "database": {"url": pg_url},
            "dataset_storage": {"type": "fsspec", "path": s3_workspace},
        }

        print(
            "Database: postgresql://userspace_default:***@localhost:5432/userspace_default"
        )
        print(f"Dataset storage: {s3_workspace}")
    else:
        config = {
            "storage": {"type": "sql"},
            "database": {"url": "sqlite:///workspace/evidently.db"},
        }
        print("Database: sqlite:///workspace/evidently.db")

    with open(output_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"Generated Evidently config at {output_path}")
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Evidently AI config")
    parser.add_argument(
        "--output",
        default="evidently_config.yaml",
        help="Output path for the config file",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Generate local SQLite config instead of PostgreSQL + S3",
    )
    args = parser.parse_args()

    generate_config(output_path=args.output, use_postgres=not args.local)
