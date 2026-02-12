#!/usr/bin/env python3
"""Populate the deployed Evidently AI dashboard with sample ML monitoring data.

Uses the Evidently 0.7.x API (Report, Dataset, DataDefinition, presets)
and uploads snapshots via RemoteWorkspace with x-api-key auth.
"""

import argparse
import datetime
import json
import os

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

# Patch the secret header name so RemoteWorkspace sends x-api-key
# instead of evidently-secret (required for Outerbounds BrowserAndApi auth)
import evidently.legacy.ui.workspace.remote as _remote_mod
import evidently.ui.workspace as _ws_mod

_remote_mod.SECRET_HEADER_NAME = "x-api-key"
_ws_mod.SECRET_HEADER_NAME = "x-api-key"

from evidently import (
    Report,
    Dataset,
    DataDefinition,
    BinaryClassification,
    Regression,
)
from evidently.presets import (
    DataDriftPreset,
    DataSummaryPreset,
    ClassificationPreset,
    RegressionPreset,
)
from evidently.ui.workspace import RemoteWorkspace


def get_auth_token() -> str:
    """Get auth token from Metaflow config."""
    try:
        from metaflow.metaflow_config_funcs import init_config

        conf = init_config()
        if conf:
            return conf["METAFLOW_SERVICE_AUTH_KEY"]
        else:
            headers = json.loads(os.environ["METAFLOW_SERVICE_HEADERS"])
            return headers.get("x-api-key", "")
    except Exception as e:
        raise RuntimeError(f"Could not get auth token: {e}")


def generate_classification_data(n_samples=1000, drift=False, seed=42):
    """Generate synthetic classification dataset with optional drift."""
    rng = np.random.RandomState(seed)

    X, y = make_classification(
        n_samples=n_samples,
        n_features=5,
        n_informative=3,
        n_redundant=1,
        random_state=seed,
    )

    df = pd.DataFrame(
        X, columns=["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"]
    )
    df["target"] = y
    noise = rng.normal(0, 0.1, n_samples)
    df["prediction"] = (df["target"] + noise > 0.5).astype(int)

    if drift:
        df["feature_1"] += rng.normal(2.0, 0.5, n_samples)
        df["feature_2"] *= 1.5
        df["feature_3"] += rng.uniform(-1, 3, n_samples)
        flip_mask = rng.random(n_samples) < 0.2
        df.loc[flip_mask, "prediction"] = 1 - df.loc[flip_mask, "prediction"]

    return df


def generate_regression_data(n_samples=1000, drift=False, seed=42):
    """Generate synthetic regression dataset."""
    rng = np.random.RandomState(seed)

    x1 = rng.normal(0, 1, n_samples)
    x2 = rng.normal(0, 1, n_samples)
    x3 = rng.uniform(-2, 2, n_samples)
    target = 3 * x1 + 2 * x2 - x3 + rng.normal(0, 0.5, n_samples)

    df = pd.DataFrame(
        {"feature_a": x1, "feature_b": x2, "feature_c": x3, "target": target}
    )

    prediction_noise = rng.normal(0, 2.0 if drift else 0.3, n_samples)
    if drift:
        df["feature_a"] += 1.5
        df["feature_b"] *= 2

    df["prediction"] = target + prediction_noise
    return df


def populate(api_url: str):
    """Populate the Evidently workspace with sample projects and reports."""

    token = get_auth_token()
    ws = RemoteWorkspace(base_url=api_url, secret=token)
    print("Connected to Evidently API")

    # ── Project 1: Classification Model Monitoring ──
    print("\n=== Creating project: Classification Model Monitoring ===")
    clf_project = ws.create_project(
        "Classification Model Monitoring",
        description="Binary classification model for customer churn. "
        "Tracks data drift and classification performance over 6 weeks.",
    )
    clf_project.save()
    print(f"  Project ID: {clf_project.id}")

    data_def_clf = DataDefinition(
        numerical_columns=["feature_1", "feature_2", "feature_3", "feature_4", "feature_5"],
        classification=[BinaryClassification(target="target", prediction_labels="prediction")],
    )

    ref_clf_df = generate_classification_data(n_samples=1000, drift=False, seed=42)
    ref_clf = Dataset.from_pandas(ref_clf_df, data_definition=data_def_clf)

    for week in range(6):
        has_drift = week >= 4
        cur_df = generate_classification_data(n_samples=500, drift=has_drift, seed=100 + week)
        cur_clf = Dataset.from_pandas(cur_df, data_definition=data_def_clf)
        ts = datetime.datetime.now() - datetime.timedelta(weeks=5 - week)

        drift_snap = Report([DataDriftPreset()]).run(reference_data=ref_clf, current_data=cur_clf)
        drift_snap._timestamp = ts
        ws.add_run(clf_project.id, drift_snap)
        print(f"  Week {week+1}: data drift (drift={has_drift})")

        perf_snap = Report([ClassificationPreset()]).run(reference_data=ref_clf, current_data=cur_clf)
        perf_snap._timestamp = ts
        ws.add_run(clf_project.id, perf_snap)
        print(f"  Week {week+1}: classification performance")

    # ── Project 2: Regression Model Monitoring ──
    print("\n=== Creating project: Regression Model Monitoring ===")
    reg_project = ws.create_project(
        "Regression Model Monitoring",
        description="Regression model for house price prediction. "
        "Tracks prediction quality and feature drift over 6 weeks.",
    )
    reg_project.save()
    print(f"  Project ID: {reg_project.id}")

    data_def_reg = DataDefinition(
        numerical_columns=["feature_a", "feature_b", "feature_c"],
        regression=[Regression(target="target", prediction="prediction")],
    )

    ref_reg_df = generate_regression_data(n_samples=1000, drift=False, seed=7)
    ref_reg = Dataset.from_pandas(ref_reg_df, data_definition=data_def_reg)

    for week in range(6):
        has_drift = week >= 3
        cur_df = generate_regression_data(n_samples=500, drift=has_drift, seed=200 + week)
        cur_reg = Dataset.from_pandas(cur_df, data_definition=data_def_reg)
        ts = datetime.datetime.now() - datetime.timedelta(weeks=5 - week)

        drift_snap = Report([DataDriftPreset()]).run(reference_data=ref_reg, current_data=cur_reg)
        drift_snap._timestamp = ts
        ws.add_run(reg_project.id, drift_snap)
        print(f"  Week {week+1}: data drift (drift={has_drift})")

        reg_snap = Report([RegressionPreset()]).run(reference_data=ref_reg, current_data=cur_reg)
        reg_snap._timestamp = ts
        ws.add_run(reg_project.id, reg_snap)
        print(f"  Week {week+1}: regression performance")

    # ── Project 3: Data Summary Monitoring ──
    print("\n=== Creating project: Data Summary Monitoring ===")
    dq_project = ws.create_project(
        "Data Summary Monitoring",
        description="Tracks data summary stats across incoming batches - "
        "distributions, missing values, feature stats.",
    )
    dq_project.save()
    print(f"  Project ID: {dq_project.id}")

    data_def_dq = DataDefinition(
        numerical_columns=["age", "income", "score"],
        categorical_columns=["category"],
    )

    for week in range(4):
        rng = np.random.RandomState(300 + week)
        n = 500
        data = pd.DataFrame(
            {
                "age": rng.normal(35, 10, n).clip(18, 80).astype(int),
                "income": rng.lognormal(10.5, 0.8, n),
                "category": rng.choice(["A", "B", "C", "D"], n),
                "score": rng.uniform(0, 100, n),
            }
        )

        if week >= 2:
            null_mask = rng.random(n) < 0.15
            data.loc[null_mask, "age"] = np.nan
            data.loc[null_mask, "income"] = np.nan

        ref_ds = Dataset.from_pandas(data.head(250), data_definition=data_def_dq)
        cur_ds = Dataset.from_pandas(data.tail(250), data_definition=data_def_dq)

        ts = datetime.datetime.now() - datetime.timedelta(weeks=3 - week)
        dq_snap = Report([DataSummaryPreset()]).run(reference_data=ref_ds, current_data=cur_ds)
        dq_snap._timestamp = ts
        ws.add_run(dq_project.id, dq_snap)
        print(f"  Week {week+1}: data summary (nulls={'yes' if week >= 2 else 'no'})")

    print("\n" + "=" * 60)
    print("Done! 3 projects created with 28 total reports.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Populate Evidently dashboard with sample data"
    )
    parser.add_argument("--url", required=True, help="Evidently API URL")
    args = parser.parse_args()

    populate(args.url)


if __name__ == "__main__":
    main()
