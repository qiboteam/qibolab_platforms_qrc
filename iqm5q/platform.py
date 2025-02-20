import pathlib

from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent
NAME = "iqm5q_qblox"
ADDRESS = "192.168.0.6"
"""Cluster ``iqm5q_qblox``."""

# the only cluster of the config
CLUSTER = {
    "qrm_rf0": (19, {"io1": [0, 1]}),
    "qrm_rf1": (20, {"io1": [2, 3, 4]}),
    "qcm_rf0": (8, {1: [1], 2: [2]}),
    "qcm_rf1": (10, {1: [3], 2: [4]}),
    "qcm_rf2": (12, {1: [0]}),
    "qcm0": (2, {1: [0], 2: [1], 3: [2], 4: [3]}),
    "qcm1": (4, {1: [4], 2: ["c1"], 4: ["c3"]}),
    "qcm2": (6, {2: ["c4"]}),
    "qcm3": (17, {1: ["c0"]}),
}
"""Connections compact representation."""


def create():
    """IQM 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(5)}
    couplers: QubitMap = {
        f"coupler_{i}": Qubit.default(f"coupler_{i}") for i in (0, 1, 3, 4)
    }

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits, couplers)
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
    instruments = {"qblox": controller, "twpa": SGS100A(address="192.168.0.35")}
    return Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, couplers=couplers
    )
