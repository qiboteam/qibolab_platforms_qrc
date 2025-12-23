from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

NAME = "qpu149"
ADDRESS = "192.168.0.2"

# in principle there is a disconnected qubit 5, and a qubit 4 which has not been
# calibrated
CLUSTER = {
    "qcm_rf2": (14, {1: [0], 2: [1]}),
    "qcm_rf1": (12, {1: [2], 2: [3]}),
    # "qcm_rf0": (10, {2: [4]}),
    "qrm_rf": (20, {"io1": [0, 1, 2, 3]}),
}
"""Connections compact representation."""

def create():
    """foundry QPU149 controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(4)}

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
    instruments = {
        "qblox": controller,
        "twpa": SGS100A(address="192.168.0.37", turn_off_on_disconnect=False),
    }
    return Hardware(
        instruments=instruments,
        qubits=qubits,
    )
