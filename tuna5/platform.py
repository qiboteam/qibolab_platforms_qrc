import pathlib

from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A
import logging

logging.basicConfig(level=logging.INFO)

FOLDER = pathlib.Path(__file__).parent
NAME = "tuna5"
ADDRESS = "192.168.0.6"

CLUSTER = {
    "qrm_rf": (19, {"io1": [0, 1, 2, 3, 4]}),
    "qcm_rf0": (13, {1: [4]}),
    "qcm_rf1": (15, {1: [2], 2:[3]}),
    "qcm_rf2": (17, {1: [0], 2: [1]}),
    "qcm0": (4, {1: ["coupler_0"], 2: ["coupler_1"], 3: ["coupler_2"], 4: ["coupler_3"]}),
    "qcm1": (6, {1: [4]}),
    "qcm2": (8, {1: [0], 2: [1], 3: [2], 4: [3]}),
}
"""Connections compact representation."""

def create():
    """TUNA-5 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(5)}
    tunable_couplers: QubitMap = {f"coupler_{i}": Qubit.coupler(i) for i in range(4)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits, tunable_couplers)
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
                update={"lo": los[i, True], "mixer": f'{q.probe}/mixer'}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": f'{q.drive}/mixer'}
            )
        
        if q.drive is not None:
            for k in [(1,2)]:
                k_str = str(k).replace(" ", "")
                logging.info(f"Adding extra drive channel for qubit {i}: {k}")
                q.drive_extra = {k: 
                    channels[q.drive].model_copy(
                        update={"lo": los[i, False], "mixer": f"{q.drive}/{k_str}/mixer"}
                    )
                }
                channels |= {f'{i}/drive/{k_str}': q.drive_extra[k]}
                logging.info(f"Added extra drive channel for qubit {i}: {k} -> {channels[f'{i}/drive/{k_str}']}")


    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
        "twpa": SGS100A(address="192.168.0.35", turn_off_on_disconnect=False),
    }
    return Platform.load(
        path=FOLDER,
        instruments=instruments,
        qubits=qubits,
        couplers=tunable_couplers,
    )
