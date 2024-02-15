import numpy as np
from qibolab import create_platform

platform = create_platform("tii1qs_xld1000")

platform.connect()

qm = platform.instruments["qm"]
qm.calibrate_mixers(list(platform.qubits.values()))

platform.disconnect()
