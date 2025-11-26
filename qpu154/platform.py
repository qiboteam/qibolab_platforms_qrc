import pathlib
 
from qibolab import Qubit, Hardware, initialize_parameters
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

ADDRESS = "192.168.0.20"
FOLDER  = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name
NUM_QUBITS = 2
ROOT = pathlib.Path.home()

# the only other cluster of the config
CLUSTER = {
    "qrm_rf0": (18, {"io1": [0, 1]}),
    "qcm_rf0": (14, {1: [0], 2: [1]}),
    "qcm0": (6, {1: [0], 2: [1], 3: [], 4: []}),
}
"""Connections compact representation."""

def create():
    """TII (QW fab) 2 qubit QPU controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(i) for i in range(NUM_QUBITS)}
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
    instruments = {"qblox": controller}# ,"twpa": SGS100A(address="192.168.0.32")} 
    return Hardware(
        instruments=instruments, qubits=qubits, #couplers=couplers
    )


if __name__ == "__main__":
    # You may need to rename the file to something different than platform.py to run this script.
    platform = create()
    parms = initialize_parameters(platform)
    (FOLDER / "parameters.json").write_text(
        parms.model_dump_json(indent=4)
    )