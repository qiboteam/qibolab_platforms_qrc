from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import ClusterMap, Twpa, build_channels
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

    # Build channels from the compact representation: this already wires LOs, mixers
    # and the TWPA pump for the standard probe/drive/acquisition channels.
    channels, twpas = build_channels(
        CLUSTER, qubits, twpa_pumps={i: "twpa" for i in qubits}
    )

    # Register the 1-2 transition drive channels. They share the physical port, LO
    # and mixer of the 0-1 drive, so a plain copy is enough.
    for q in qubits.values():
        assert q.drive is not None
        for extra in q.drive_extra.values():
            channels[extra] = channels[q.drive].model_copy()

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels, twpas=twpas)
    return Hardware(instruments={"qblox": controller}, qubits=qubits)
