import pathlib

from qibolab import ConfigKinds, Platform, Qubit
from qibolab._core.instruments.qblox.channels import QbloxConfigs
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import map_ports
from qibolab._core.platform.platform import QubitMap

# from qibolab.instruments.qblox import Cluster, QbloxConfigs, map_ports
from qibolab.instruments.rohde_schwarz import SGS100A

# Register Qblox-specific configurations for parameters loading
ConfigKinds.extend([QbloxConfigs])

FOLDER = pathlib.Path(__file__).parent
NAME = "iqm5q_qblox"
ADDRESS = "192.168.0.6"
"""Cluster ``iqm5q_qblox``."""

# the only cluster of the config
CLUSTER = {
    "qrm_rf0": (19, {"io1": ["q0", "q1"]}),
    "qrm_rf1": (20, {"io1": ["q2", "q3", "q4"]}),
    "qcm_rf0": (8, {1: ["q1"], 2: ["q2"]}),
    "qcm_rf1": (10, {1: ["q3"], 2: ["q4"]}),
    "qcm_rf2": (12, {1: ["q0"]}),
    "qcm0": (2, {1: ["q0"], 2: ["q1"], 3: ["q2"], 4: ["q3"]}),
    "qcm1": (4, {1: ["q4"], 2: ["c1"], 4: ["c3"]}),
    "qcm2": (6, {2: ["c4"]}),
    "qcm3": (17, {1: ["c0"]}),
}
"""Connections compact representation."""


def create():
    """IQM 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {f"q{i}": Qubit.default(f"q{i}") for i in range(5)}
    couplers: QubitMap = {f"c{i}": Qubit.default(f"c{i}") for i in (0, 1, 3, 4)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits, couplers)

    # update channel information beyond connections
    for q in qubits.values():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": "twpa"}
            )

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller, "twpa": SGS100A(address="192.168.0.35")}
    return Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, couplers=couplers
    )
