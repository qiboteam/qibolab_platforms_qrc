- Make sure that you have your virtual environment setup and activated (the one that you use for running calibration experiments).
- Make sure that your `QIBOLAB_PLATFORMS` environment variable points to this copy of the `qibolab_platforms_qrc` repository.
- Change working directory to here:
```bash
cd ${QIBOLAB_PLATFORMS}/qpu118/calibrate_mixers
```
- Run the calibration script through slurm (make sure you have a _qpu118_mixers.log log file in your local logs folder):
```bash
# Create log directory and file if they don't exist
mkdir -p ~/logs && touch ~/logs/_qpu118_mixers.log
sbatch -v -J recal -p qpu_xld1000 -o ~/logs/_qpu118_mixers.log recal.sh
```
