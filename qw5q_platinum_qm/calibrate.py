from qibolab import create_platform

platform = create_platform("qw5q_platinum")

platform.connect()

qm = platform.instruments["qm"]
qm.calibrate_mixers(list(platform.qubits[0]))

platform.disconnect()
