#!/bin/bash
# Deploy Evidently AI app to Outerbounds

set -e

echo "================================================"
echo "Deploying Evidently AI to Outerbounds Apps"
echo "================================================"
echo ""

echo "Deploying Evidently UI (Browser auth)..."
outerbounds app deploy --config-file evidently-ui.yaml

echo ""
echo "Deployment initiated!"
echo ""

echo "================================================"
echo "Deployment Status"
echo "================================================"
outerbounds app list | grep evidently

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Wait for the app to become ready (check 'outerbounds app list')"
echo "2. Open the evidently-ui URL in your browser"
echo "3. Use the test script: python test_app.py --url <EVIDENTLY_URL>"
echo ""
