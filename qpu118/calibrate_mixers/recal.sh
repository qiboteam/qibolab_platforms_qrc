#!/bin/bash
# SBATCH --job-name=recal
# SBATCH --partition=qpu_xld1000

# export QIBOLAB_PLATFORMS=~qibolab_platforms_qrc
export QIBO_PLATFORM=qpu118

python calibrate_mixers_qpu118.py
