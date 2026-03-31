#!/bin/bash

# ==========================================
# Load Apptainer module
module load StdEnv/2023 apptainer/1.3.5
# ==========================================

echo "Starting MSA download..."

# Make sure the output directory exists
mkdir -p msas

# Run ColabFold Batch (for downloading MSA)
# Note: This step doesn't require GPU, so --nv is removed
apptainer exec \
    -B $PWD:$PWD \
    -B $PWD/colabfold_weights:/cache \
    -B /etc/pki:/etc/pki \
    colabfold_1.5.5.sif \
    colabfold_batch \
    $PWD/input \
    $PWD/msas \
    --num-recycle 0 \
    --model-type alphafold2_multimer_v3 \
    --msa-only

echo "MSA download completed. Please check if .a3m files are present in the msas folder."