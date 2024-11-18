#!/bin/bash

if [ -d recal_reports ]; then
    re -r recal_reports
fi

mkdir recal_reports

qq run ./runcard_frequencies.yml -o ./recal_reports/recal_frequencies -f

python calibrate_mixers.py

qq run ./runcard_1q_gates.yml -o ./recal_reports/recal_1q_gates -f
