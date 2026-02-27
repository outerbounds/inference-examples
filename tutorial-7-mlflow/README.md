# Tutorial 7 — MLflow on Outerbounds

Run an MLflow Tracking Server as an Outerbounds app with a persistent PostgreSQL backend, then log experiments from a Metaflow flow.

## What's in here

| File | Purpose |
|---|---|
| `config.yaml` | Outerbounds app config — deploys MLflow server with `persistence: postgres` |
| `start_mlflow.sh` | Startup script that wires Postgres credentials into `mlflow server` |
| `generate_pg_url.py` | Reads Metaflow config to build the PostgreSQL connection string |
| `train_flow.py` | Metaflow flow that trains a dummy Ridge model and logs metrics + registers the model in MLflow |

## Deploy the MLflow server

```bash
outerbounds app deploy --config-file config.yaml
```

This deploys the MLflow UI on port 5000 with **Browser** auth (accessible via your browser). The `persistence: postgres` flag provisions a PostgreSQL database automatically — experiment data survives restarts and redeployments.

## Run the training flow

```bash
python train_flow.py run
```

The flow:
1. Generates a toy regression dataset
2. Trains a Ridge regression model
3. Logs params (`alpha`, `n_samples`, `n_features`), metrics (`mse`, `r2`), and the model artifact to MLflow
4. Registers the model as `outerbounds-ridge` in the MLflow Model Registry

The flow auto-discovers the MLflow server URL via `metaflow.apps.AppDeployer`. You can also pass a custom URI:

```bash
python train_flow.py run --tracking-uri https://your-mlflow-url
```

## About `persistence: postgres`

This is a config-file-only flag that provisions a PostgreSQL sidecar for your app. Key details:

- **Host:** `localhost:5432`
- **Database:** `userspace_default`
- **Username:** `userspace_default`
- **Password:** Pulled from `METAFLOW_SERVICE_AUTH_KEY` in the Metaflow config
- **Data survives** app restarts and redeployments

MLflow uses it as the `--backend-store-uri` to persist experiments, runs, params, metrics, and registered models.

## Cleanup

```bash
outerbounds app delete --name mlflow-tracking
```
