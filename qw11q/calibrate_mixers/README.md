- Make sure that you have your virtual environment setup and activated (the one that you use for running calibration experiments).
- Make sure that your `QIBOLAB_PLATFORMS` environment variable points to this copy of the `qibolab_platforms_qrc` repository.
- Change working directory to here:
```
cd qibolab_platforms_qrc/qw11q/calibrate_mixers
```
- Run the calibration script through slurm (make sure you have a _qw11q_mixers.log log file in your local logs folder):
```
sbatch -v -J recal -p qw11q -o ~/logs/_qw11q_mixers.log ./recal.sh
```
