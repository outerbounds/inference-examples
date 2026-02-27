#!/usr/bin/env python3
"""Generate PostgreSQL connection URL from Metaflow/Outerbounds credentials.

On Outerbounds with `persistence: postgres`, a PostgreSQL database is
available at localhost:5432. Credentials come from the Metaflow config.

MLflow gets its own schema ("mlflow") to avoid Alembic migration conflicts
with other apps (e.g. Evidently) sharing the same database.
"""

import os
import json
import sys
from urllib.parse import quote_plus


def get_metaflow_token():
    metaflow_home = os.environ.get(
        "METAFLOW_HOME", os.path.expanduser("~/.metaflowconfig")
    )
    config_path = os.path.join(metaflow_home, "config.json")

    try:
        with open(config_path, "r") as f:
            conf = json.load(f)
            return conf["METAFLOW_SERVICE_AUTH_KEY"]
    except FileNotFoundError:
        print(f"ERROR: Config not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    except KeyError:
        print("ERROR: METAFLOW_SERVICE_AUTH_KEY not in config", file=sys.stderr)
        sys.exit(1)


def ensure_mlflow_schema(token):
    """Create the 'mlflow' schema if it doesn't exist."""
    import psycopg2

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="userspace_default",
        user="userspace_default",
        password=token,
        sslmode="disable",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("CREATE SCHEMA IF NOT EXISTS mlflow")
    cur.close()
    conn.close()


def get_postgres_url(token):
    # Use options=-csearch_path=mlflow to isolate MLflow's tables
    options = quote_plus("-csearch_path=mlflow")
    return (
        f"postgresql://userspace_default:{token}@localhost:5432"
        f"/userspace_default?sslmode=disable&options={options}"
    )


if __name__ == "__main__":
    token = get_metaflow_token()
    ensure_mlflow_schema(token)
    print(get_postgres_url(token))
