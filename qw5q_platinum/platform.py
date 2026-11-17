from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import ClusterMap, Twpa
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap

NAME = "qw5q_platinum"
ADDRESS = "192.168.0.21"

CLUSTER: ClusterMap = {
    "qrm_rf": (18, {"io1": [0, 1, 2, 3, 4]}),
    "qcm_rf0": (12, {1: [0], 2: [1]}),
    "qcm_rf1": (10, {1: [2], 2: [3]}),
    "qcm_rf2": (8, {1: [4], 2: [Twpa()]}),
    "qcm0": (16, {1: [0], 2: [1], 3: [2], 4: [3]}),
    "qcm1": (14, {1: [4]}),
}
"""Connections compact representation."""


def create() -> Hardware:
    """QW Soprano architecture, controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(5)}
    # all the qubits are read out through the same transmission line, amplified by the
    # same TWPA
    for i, q in qubits.items():
        q.drive_extra[(1, 2)] = f"{i}/drive/(1, 2)"

    # Create channels and connect to instrument ports
    channels, _ = map_ports(CLUSTER, qubits)
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
        if q.drive_extra is not None:
            for k in q.drive_extra.keys():
                channels |= {
                    q.drive_extra[k]: channels[q.drive].model_copy(
                        update={"lo": los[i, False]}
                    )
                }

    controller = Cluster.from_map(
        NAME, ADDRESS, CLUSTER, qubits, twpa_pumps={i: "twpa" for i in qubits}
    )
    return Hardware(instruments={"qblox": controller}, qubits=qubits)
