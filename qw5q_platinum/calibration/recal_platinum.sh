#!/bin/bash
# copied from iqm11q and not tested

if [ -d recal_reports ]; then
    re -r recal_reports
fi

mkdir recal_reports

qq run ./runcard_frequencies_platinum.yml -o ./recal_reports/recal_frequencies_platinum -f
qq update ./recal_reports/recal_frequencies_platinum

python calibrate_mixers_platinum.py

qq run ./runcard_1q_gates_platinum.yml -o ./recal_reports/recal_1q_gates_platinum -f
