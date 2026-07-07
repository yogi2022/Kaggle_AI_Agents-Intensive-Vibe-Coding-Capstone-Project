#!/usr/bin/env bash
# Remove cloud resources to keep spend at zero (course Day 5 guidance).
set -euo pipefail
SERVICE="${1:-berean}"
REGION="${2:-us-central1}"
echo "Deleting Cloud Run service '$SERVICE' in $REGION ..."
gcloud run services delete "$SERVICE" --region "$REGION" --quiet || true
echo "If you deployed the agent to Agent Runtime, delete it via the Agents CLI / console too."
echo "Then confirm billing shows no active resources."
