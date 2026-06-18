import pathlib

from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent
NAME = "qpu175"
ADDRESS = "192.168.0.20"

CLUSTER = {
    "qrm_rf": (19, {"io1": [0, 1, 2, 3]}),
    "qcm_rf0": (14, {1: [0], 2: [2]}),
    "qcm_rf1": (8, {1: [1], 2: [3]}),
}
"""Connections compact representation."""


def create():
    """qpu 175 chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(4)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)
    mixers = infer_mixers(CLUSTER)

    # update channel information beyond connections
    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": "twpa"}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True], "mixer": mixers[i, True]}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": mixers[i, False]}
            )

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
        "twpa": SGS100A(address="192.168.0.32", turn_off_on_disconnect=False),
    }
    return Platform.load(
        path=FOLDER,
        instruments=instruments,
        qubits=qubits,
    )
