# Tutorial 5: Evidently AI on Outerbounds

Deploy [Evidently AI](https://docs.evidentlyai.com/) as an Outerbounds App for ML monitoring and observability.

## What's Included

| File | Description |
|------|-------------|
| `evidently-ui.yaml` | Outerbounds App config (deploy config) |
| `run_evidently.py` | Python wrapper that imports SQL components before starting the Evidently UI |
| `generate_config.py` | Generates Evidently config from Metaflow/Outerbounds credentials |
| `start_evidently.sh` | Entrypoint script that generates config and starts the service |
| `deploy.sh` | Convenience script to deploy the app |
| `test_app.py` | Test script to verify the deployment |
| `evidently_config.yaml` | Default local SQLite config (overwritten at deploy time) |
| `Makefile` | Common commands for local dev and deployment |

## Quick Start

### Deploy to Outerbounds

```bash
cd tutorial-5-evidently
outerbounds app deploy --config-file evidently-ui.yaml
```

Or use the Makefile:

```bash
make deploy
```

### Run Locally

```bash
make install     # install dependencies
make run-local   # start Evidently UI on localhost:8000
```

### Test

```bash
# Test local instance
make test-local

# Test deployed instance
make test-remote URL=https://evidently-ui-xyz.outerbounds.xyz
make populate URL=https://evidently-ui-xyz.outerbounds.xyz
```

## How It Works

1. **`start_evidently.sh`** runs at container startup
2. **`generate_config.py`** reads Metaflow credentials to build a config with PostgreSQL (via `persistence: postgres`) and S3 dataset storage
3. **`run_evidently.py`** imports the SQL storage components (required for the `database` config section) and starts the Evidently UI server

When deployed on Outerbounds, the app uses:
- **PostgreSQL** (via `persistence: postgres` in the app config) for metadata storage
- **S3** (via Metaflow's `DATASTORE_SYSROOT_S3`) for dataset storage
- **BrowserAndApi** auth so the UI is accessible in the browser and via API
