from qibolab import ConfigKinds, Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

NAME = "qpu118"
ADDRESS = "192.168.0.21"

# the only cluster of the config

# probe line attached to L3-31
# acquisition line attached to L2-25
# qubit 0 attached to L3-27
# qubit 1 attached to L3-25
# qubit 2 attached to L3-26
CLUSTER = {
    "qrm_rf0": (18, {"io1": [0, 1, 2]}),
    "qcm_rf0": (12, {1: [2], 2: [0]}), 
    "qcm_rf1": (10, {1: [1]}),
}
"""Connections compact representation."""


def create():
    """QW5Q controlled with a Qblox cluster."""
    qubits: QubitMap = {i: Qubit.default(f"{i}") for i in range(3)}

    # Add extra drive channels for e-f transitions
    # for i in range(3):
    #     qubits[i].drive_extra[1, 2] = f"{i}/drive_ef"
    qubits[0].drive_extra[1] = "01/drive" # CR: control 0, target 1
    qubits[1].drive_extra[2] = "12/drive" # CR: control 1, target 2
    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits)
    los = infer_los(CLUSTER)
    mixers = infer_mixers(CLUSTER)

    # update channel information beyond connections
    for i, q in qubits.items():
        if q.probe is not None:
            channels[q.probe] = channels[q.probe].model_copy(
                update={"lo": los[i, True], "mixer": mixers[i, True]}
            )
        if q.drive is not None:
            channels[q.drive] = channels[q.drive].model_copy(
                update={"lo": los[i, False], "mixer": mixers[i, False]}
            )
        if q.drive_extra is not None and q.drive is not None:
            for k, de in q.drive_extra.items():
                channels[de] = channels[q.drive].model_copy(
                    update={"lo": los[i, False], "mixer": mixers[i, False]}
                )

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
    }
    return Hardware(instruments=instruments, qubits=qubits)
