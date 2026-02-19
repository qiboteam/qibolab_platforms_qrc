#!/bin/bash
# SBATCH --job-name=recal
# SBATCH --partition=agnostic2

# export QIBOLAB_PLATFORMS=~qibolab_platforms_qrc
# export QIBO_PLATFORM=QPU118

python calibrate_mixers_qpu118.py
