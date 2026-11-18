from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import ClusterMap, Twpa
from qibolab._core.platform.platform import QubitMap

NAME = "tuna5"
ADDRESS = "192.168.0.6"

CLUSTER: ClusterMap = {
    "qrm_rf0": (19, {"io1": [0, 1]}),
    "qrm_rf1": (20, {"io1": [2, 3, 4]}),
    "qcm_rf0": (13, {1: [4], 2: [Twpa()]}),
    "qcm_rf1": (15, {1: [2], 2: [3]}),
    "qcm_rf2": (17, {1: [0], 2: [1]}),
    "qcm0": (
        4,
        {1: ["coupler_0"], 2: ["coupler_1"], 3: ["coupler_2"], 4: ["coupler_3"]},
    ),
    "qcm1": (6, {1: [4]}),
    "qcm2": (8, {1: [0], 2: [1], 3: [2], 4: [3]}),
}
"""Connections compact representation."""


def create() -> Hardware:
    """TUNA-5 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(5)}
    for i, q in qubits.items():
        q.drive_extra[(1, 2)] = f"{i}/drive/(1, 2)"
    tunable_couplers: QubitMap = {f"coupler_{i}": Qubit.coupler(i) for i in range(4)}

    controller = Cluster.from_map(
        NAME,
        ADDRESS,
        CLUSTER,
        qubits,
        couplers=tunable_couplers,
        twpa_pumps={i: "twpa" for i in qubits},
    )
    for q in qubits.values():
        for channel in q.drive_extra.values():
            controller.channels[channel] = controller.channels[q.drive].model_copy()

    return Hardware(
        instruments={"qblox": controller},
        qubits=qubits,
        couplers=tunable_couplers,
    )
