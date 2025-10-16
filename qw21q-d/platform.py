import pathlib

from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

NAME = "qw21q-d"
ADDRESS = "192.168.0.21"

# the only cluster of the config
CLUSTER = {
    "qrm_rf0": (18, {"io1": [1, 2, 3, 4, 5]}),
    "qcm_rf0": (12, {1: [1], 2: [2]}),
    "qcm_rf1": (10, {1: [3], 2: [4]}),
    "qcm_rf2": (8, {1: [5]}),
    "qcm0": (16, {1: [1], 2: [2], 3: [3], 4: [4]}),
    "qcm1": (14, {1: [5]}),
}
"""Connections compact representation."""


def create():
    """IQM 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(1, 6)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)

    # update channel information beyond connections
    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": "twpa"}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True]}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False]}
            )

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller, "twpa": SGS100A(address="192.168.0.33")}
    return Hardware(instruments=instruments, qubits=qubits)
