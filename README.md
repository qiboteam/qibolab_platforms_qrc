# qibolab_platforms_qrc

This repository contains platforms that are currently available in the TII QRC Quantum Computing lab.

In order to use these platforms, one needs to:

1. Install the latest version of [qibolab](https://github.com/qiboteam/qibolab).
2. Clone this repository
```sh
git clone https://github.com/qiboteam/qibolab_platforms_qrc
```
3. Point the environment variable `QIBOLAB_PLATFORMS` to the directory where `qibolab_platforms_qrc` was cloned. For example, if it was cloned in the home directory:
```sh
export QIBOLAB_PLATFORMS=~/qibolab_platforms_qrc
```
The last step needs to executed for every new terminal instance. To avoid having to do this, in linux you can add the above command to your `~/.bashrc`.

The `main` branch of this repository should contain the latest available platforms.
If your platform is in a branch other than `main`, in addition to the above steps, you need to switch your local `qibolab_platforms_qrc` repository to your branch. 
If your platform works, you can open a pull request to merge it to main.
