from qibolab import ConfigKinds, Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import map_ports
from qibolab._core.platform.platform import QubitMap

NAME = "qw21q-d"
ADDRESS = "192.168.0.2"

# the only cluster of the config
CLUSTER = {
    "qcm0": (6, {1: ["D1"]}),
}
"""Connections compact representation."""


def create():
    """QW5Q controlled with a Qblox cluster."""
    qubits: QubitMap = {f"D{i}": Qubit.default(f"D{i}") for i in range(1, 2)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller}
    return Hardware(instruments=instruments, qubits=qubits)
