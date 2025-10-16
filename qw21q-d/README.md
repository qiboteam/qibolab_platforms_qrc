# qw21q - line D

The Qblox cluster connected to this line is flashed with v0.11.0 of the Qblox firmware.

By the official [Compatibility Matrix](https://pypi.org/project/qblox-instruments/)
published by Qblox this means that the v0.16.0 of the `qblox-instruments` Python package
is required.

Please install it with:

```sh
pip install qblox-instruments==0.16.0
```

An TWPA pump from Rohde-Schwarz is also part of the setup. The required dependencies can
be obtained with

```sh
pip install qcodes qcodes_contrib_drivers pyvisa-py
```

Any recent version is assumed to be good enough.
