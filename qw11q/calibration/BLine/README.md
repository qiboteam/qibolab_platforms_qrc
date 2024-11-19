- Make sure that you have your virtual environment setup and activated (the one that you use for running calibration experiments).
- Make sure that your `QIBOLAB_PLATFORMS` environment variable points to this copy of the `qibolab_platforms_qrc` repository.
- Change working directory to here:
```
cd qibolab_platforms_qrc/qw11q/calibration/BLine/
```
- Run the calibration script through slurm:
```
sbatch -v -J recal -p qw11q ./recal.sh
```
- On a successfull run this will generate two reports under the `./recal_reports` directory. Previous reports will be ovewritten.
- The report under `./recal_reports/recal_frequencies` will be used automatically to update the platform,
- However the report under `./recal_reports/recal_frequencies/recal_1q_gates` will not be used automatically to update the platform.
You will need to do this manually, after checking that the report is fine:
```
-qq update ./recal_reports/recal_1q_gates
```
