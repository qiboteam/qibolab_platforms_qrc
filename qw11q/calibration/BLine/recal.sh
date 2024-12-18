#!/bin/bash

if [ -d recal_reports ]; then
    rm -r recal_reports
fi

mkdir recal_reports

qq run ./runcard_frequencies.yml -o ./recal_reports/recal_frequencies -f
qq update ./recal_reports/recal_frequencies

python calibrate_mixers.py

qq run ./runcard_1q_gates.yml -o ./recal_reports/recal_1q_gates -f
