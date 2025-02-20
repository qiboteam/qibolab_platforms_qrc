"""Debugging platform for Qblox development."""

from qibolab import Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import map_ports

NAME = "qblox-test"
ADDRESS = "192.168.0.21"
"""Cluster ``QBC21``."""

# the only cluster of the config
CLUSTER = {
    "qcm": (12, {1: [0]}),
    "qcm_rf": (15, {"io1": [0]}),
    "qrm_rf": (16, {"i1": [0]}),
    "qrm_rf_lo": (20, {"io1": [1]}),
}
"""Connections compact representation."""


def create():
    """Platform creation."""
    qubits = {i: Qubit.default(i) for i in range(2)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)

    return Hardware(instruments={"qblox": controller}, qubits=qubits)
