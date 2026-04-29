import pathlib

from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

ADDRESS = "192.168.0.6"
FOLDER = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name

qubit_names = [0, 1, 2, 3, 4]

CLUSTER = {
    "qcm_rf0": (15, {1: [0], 2: [1]}),
    "qcm_rf1": (14, {1: [2], 2: [4]}),
    "qcm_rf2": (8, {1: [3]}),
    "qrm_rf0": (19, {"io1": [0, 1, 2, 3, 4]}),
}


def create():
    """QPU controlled with a Qblox cluster."""
    qubits: QubitMap = {name: Qubit.default(name) for name in qubit_names}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)
    mixers = infer_mixers(CLUSTER)

    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": None}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True], "mixer": mixers[i, True]}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": mixers[i, False]}
            )

    controller = Cluster(name=PLATFORM, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
        "twpa": SGS100A(address="192.168.0.35", turn_off_on_disconnect=False),
    }

    return Platform.load(
        path=FOLDER,
        instruments=instruments,
        qubits=qubits,
    )
