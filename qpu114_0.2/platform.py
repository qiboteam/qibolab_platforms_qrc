import pathlib

from qibolab import (
    Hardware,
    Qubit,
)
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.parameters import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

ADDRESS = "192.168.0.2"
FOLDER  = pathlib.Path(__file__).parent
NAME = FOLDER.name
NUM_QUBITS = 3

CLUSTER = {
    "qcm_rf0": (2, {"o1": [2]}),  # 
    "qcm_rf1": (8, {"o1": [0],"o2": [1]}),  # q0, q1 
    "qrm_rf0": (3, {"io1": [f'q{i}' for i in range(NUM_QUBITS)]}),  # feedline   
}
"""Connections compact representation."""

def create():
    """Platform creation."""
    qubits: QubitMap = {
        0: Qubit.default(0, ["prove", "acquisition", "drive"]),
        1: Qubit.default(1, ["prove", "acquisition", "drive"]),
        2: Qubit.default(2, ["prove", "acquisition", "drive"])
    }

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

    return Hardware(instruments={"qblox": controller}, qubits=qubits)