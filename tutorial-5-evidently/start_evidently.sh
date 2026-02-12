#!/bin/bash
# Start Evidently AI service with configuration from Metaflow/Outerbounds credentials.
# This follows the same pattern as Arize Phoenix's start_phoenix.sh.

set -e

echo "============================================================"
echo "Starting Evidently AI"
echo "============================================================"

CONFIG_PATH="evidently_config.yaml"

# Generate Evidently config from Metaflow credentials
echo "Reading Metaflow configuration..."
python generate_config.py --output "$CONFIG_PATH"

# Verify config was generated
if [ ! -f "$CONFIG_PATH" ]; then
    echo "ERROR: Failed to generate Evidently config" >&2
    exit 1
fi

echo ""
echo "Host: 0.0.0.0"
echo "Port: 8000"
echo "Config: $CONFIG_PATH"
echo "============================================================"
echo ""

# Start Evidently UI service via wrapper (imports SQL components first)
python run_evidently.py \
    --host 0.0.0.0 \
    --port 8000 \
    --conf-path "$CONFIG_PATH"
