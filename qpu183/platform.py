import pathlib

from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A
import logging
import rich

FOLDER = pathlib.Path(__file__).parent
NAME = "qpu183"
ADDRESS = "192.168.0.20"
NUM_QUBITS = 4

if NUM_QUBITS >= 4:
    qubit_names = [i + 4 for i in range(NUM_QUBITS)]
else:
    qubit_names = [i for i in range(NUM_QUBITS)]

CLUSTER = {
    # "qrm_rf0": (18, {"io1": [0, 1, 2, 3]}),
    # "qcm_rf0": (14, {1: [0], 2: [1]}),
    # "qcm_rf1": (12, {1: [2], 2: [3]}),
    "qrm_rf1": (20, {"io1": [4, 5, 6, 7]}),
    "qcm_rf2": (10, {1: [4], 2: [5]}),
    "qcm_rf3": (8, {1: [6], 2: [7]})
}
"""Connections compact representation."""


def create():
    """qpu 183 chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in qubit_names}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)

    logging.info(rich.print(channels))

    # update channel information beyond connections
    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": "twpa"}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True], "mixer": f"{i}/probe/mixer"}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": f"{i}/drive/mixer"}
            )
        logging.info(rich.print(q.acquisition))
        # logging.info(rich.inspect(channels[q.acquisition]))

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
        # "twpa0": SGS100A(address="192.168.0.36", turn_off_on_disconnect=False),
        "twpa": SGS100A(address="192.168.0.32", turn_off_on_disconnect=False),
    }
    return Platform.load(
        path=FOLDER,
        instruments=instruments,
        qubits=qubits,
    )
