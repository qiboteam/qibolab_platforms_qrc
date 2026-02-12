import pathlib
import rich
from qibolab import Qubit, Hardware, initialize_parameters
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

ADDRESS = "192.168.0.20"
FOLDER  = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name
NUM_QUBITS = 5
ROOT = pathlib.Path.home()

# the only other cluster of the config
CLUSTER = {
    "qrm_rf0": (18, {"io1": [f"D{i}" for i in range(NUM_QUBITS)]}),
    "qcm_rf0": (14, {1: ["D1"], 2: []}),
    "qcm_rf1": (12, {1: ["D3"], 2: ["D4"]}),
    "qcm_rf2": (10, {1: [], 2: []}),
    # "qcm0": (6, {1: [0], 2: [1], 3: [], 4: []}),
}
"""Connections compact representation."""

qubit_names = [f"D{i}" for i in range(NUM_QUBITS)]
qubit_names = ["D1", "D3","D4"]

def create():
    """TII 5 qubit QPU controlled with a Qblox cluster, with TWPA pump pump activation."""
    qubits: QubitMap = {qubit_name: Qubit.default(qubit_name) for qubit_name in qubit_names}
    channels = map_ports(CLUSTER, qubits) # couplers)
    los = infer_los(CLUSTER)

    # update channel information
    for i, q in qubits.items():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": None}
            )
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True], "mixer": f"{i}/probe/mixer"}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": f"{i}/drive/mixer"}
            )

        if q.drive is not None and (1,2) not in q.drive_extra:
            q.drive_extra[(1,2)] = f"{i}/drive_ef"

        if q.drive_extra is not None and q.drive is not None:
            for k, de in q.drive_extra.items():
                channels[de] = channels[q.drive].model_copy(
                    update={"lo": los[i, False], "mixer": f"{i}/drive_ef/mixer"}
                )
    
    controller = Cluster(name=PLATFORM, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller ,"twpa": SGS100A(address="192.168.0.32")} 
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