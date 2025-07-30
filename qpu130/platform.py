import pathlib
 
from qibolab import Platform, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

ADDRESS = "192.168.0.2"
FOLDER  = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name
NUM_QUBITS = 4

ROOT = pathlib.Path.home()

# the only other cluster of the config
CLUSTER = {
    "qrm_rf0": (18, {"io1": [0, 1, 2,3]}),
    #"qrm_rf1": (20, {"io1": [2, 3, 4]}),
    "qcm_rf0": (4, {1: [0], 2: [1]}),
    "qcm_rf1": (6, {1: [2], 2: [3]}),
    #"qcm_rf2": (8, {1: [0]}),
    #"qcm_rf3": (8, {1: [0]}),
    
}
"""Connections compact representation."""

def create():
    """IQM 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(NUM_QUBITS)}
    #couplers: QubitMap = {f"coupler_{i}": Qubit.coupler(i) for i in (0, 1, 3, 4)}

    channels = map_ports(CLUSTER, qubits) # couplers)
    los = infer_los(CLUSTER)
    
    # update channel information beyond connections
    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": None}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True]}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False]}
            )
 
    controller = Cluster(name=PLATFORM, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller}
    return Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, #couplers=couplers
    )