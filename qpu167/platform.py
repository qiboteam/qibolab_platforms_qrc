import pathlib
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

qubit_names = ['q0', 'q1', 'q2', 'q3', 'q4']

CLUSTER = {
    "qcm_rf0": (10, {1: ['q0'], 2: []}),
    "qcm_rf1": (12, {1: ['q1'], 2: []}),
    "qcm_rf2": (14, {1: ['q2', 'q3', 'q4'], 2: []}),
    "qrm_rf0": (18, {"io1": ['q0', 'q1', 'q2', 'q3', 'q4']}),
}
"""Connections derived from hardware_config connectivity."""


def create():
    """QPU controlled with a Qblox cluster."""
    qubits: QubitMap = {name: Qubit.default(name) for name in qubit_names}
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)

    connections = [('q0', 'q1')]

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

        for c  in connections:
            if i in c:
                t = c[0] if c[0]!=i else c[1]
                if t not in q.drive_extra:
                    q.drive_extra[t] = f"{i}/drive_{t}"

        if q.drive is not None and (1, 2) not in q.drive_extra:
            q.drive_extra[(1, 2)] = f"{i}/drive_ef"

        if q.drive_extra is not None and q.drive is not None:
            for k, de in q.drive_extra.items():
                channels[de] = channels[q.drive].model_copy(
                    update={"lo": los[i, False], "mixer": f"{de}/mixer"}
                )        

    controller = Cluster(name=PLATFORM, address=ADDRESS, channels=channels)
    instruments = {"qblox": controller}#, "twpa": SGS100A(address="192.168.0.32")}
    return Hardware(instruments=instruments, qubits=qubits)


if __name__ == "__main__":
    platform = create()
    parms = initialize_parameters(platform)
    (FOLDER / "default_parameters.json").write_text(parms.model_dump_json(indent=4))
