#!/bin/bash

# Script to package the Antarbhukti-LLM artefact for SEFM'26 submission.
# Produces two required deliverables:
#   1. antarbhukti_artefact.zip  — the source archive
#   2. antarbhukti-image.tar     — the Docker image (run separately, see below)

set -e  # Exit on error

OUTPUT_ZIP="antarbhukti_artefact.zip"

echo "=================================================="
echo " Antarbhukti-LLM Artefact Packaging Script"
echo "=================================================="

# --- Step 1: Package source files ---
echo ""
echo "[1/2] Packaging source files into $OUTPUT_ZIP ..."

zip -r "$OUTPUT_ZIP" . \
  -x ".*" \
  -x "*/.*" \
  -x "__pycache__/*" \
  -x "*/__pycache__/*" \
  -x "*.pyc" \
  -x "*.pyo" \
  -x "*.zip" \
  -x "*.tar" \
  -x "*.egg-info/*" \
  -x "*.egg" \
  -x "antarbhukti-env/*" \
  -x "venv/*" \
  -x ".venv/*" \
  -x "outputs/*" \
  -x "uploads/*" \
  -x "output/*" \
  -x "artefact-submission-guidelines.pdf" \
  -x "artefact_text.txt" \
  -x "Rhpl-V1.pptx" \
  -x "*.pptx" \
  -x "src/antarbhukti/config.json" \
  -x "DatasetCreation/*" \
  -x "orig/*" \
  -x "mod/*" \
  -x "bench_backup/*" \
  -x "test_benchmarkBatch/*" \
  -x "data/*" \
  -x "*.jsonl"

echo "   ✅ Source archive created: $OUTPUT_ZIP"

# --- Step 2: Build and save the Docker image ---
echo ""
echo "[2/2] Building Docker image (antarbhukti-app) ..."
docker build -t antarbhukti-app .

echo "   Saving Docker image to antarbhukti-image.tar ..."
docker save -o antarbhukti-image.tar antarbhukti-app

echo "   ✅ Docker image saved: antarbhukti-image.tar"

# --- Summary ---
echo ""
echo "=================================================="
echo " DONE. Submit both of the following to EasyChair:"
echo "   - $OUTPUT_ZIP            (source archive)"
echo "   - antarbhukti-image.tar  (Docker image)"
echo ""
echo " Or, alternatively, push the Docker image to Docker Hub:"
echo "   docker tag antarbhukti-app <your-dockerhub-username>/antarbhukti-app:latest"
echo "   docker push <your-dockerhub-username>/antarbhukti-app:latest"
echo ""
echo " ⚠️  IMPORTANT: src/antarbhukti/config.json (API keys) was intentionally"
echo "    excluded from the zip. Provide reviewer credentials separately."
echo "=================================================="
