from qibolab import ConfigKinds, Hardware, Qubit
from qibolab._core.instruments.qblox.cluster import Cluster
from qibolab._core.instruments.qblox.config import QbloxIqMixerConfig
from qibolab._core.instruments.qblox.platform import infer_los, infer_mixers, map_ports
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

NAME = "qw21q-d"
ADDRESS = "192.168.0.2"

# the only cluster of the config
CLUSTER = {
    "qrm_rf0": (18, {"io1": ["D1", "D2", "D3", "D4", "D5"]}),
    "qcm_rf0": (12, {1: ["D1"], 2: ["D2"]}),
    "qcm_rf1": (10, {1: ["D3"], 2: ["D4"]}),
    "qcm_rf2": (6, {1: ["D5"]}),
    "qcm0": (16, {1: ["D1"], 2: ["D2"], 3: ["D3"], 4: ["D4"]}),
    "qcm1": (14, {1: ["D5"]}),
}
"""Connections compact representation."""

ConfigKinds.extend([QbloxIqMixerConfig])


def create():
    """QW5Q controlled with a Qblox cluster."""
    qubits: QubitMap = {f"D{i}": Qubit.default(f"D{i}") for i in range(1, 6)}

    # Add extra drive channels for e-f transitions
    for i in range(1, 6):
        qubits[f"D{i}"].drive_extra[1, 2] = f"D{i}/drive_ef"
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
        if q.drive_extra is not None and q.drive is not None:
            for k, de in q.drive_extra.items():
                channels[de] = channels[q.drive].model_copy(
                    update={"lo": los[i, False], "mixer": mixers[i, False]}
                )

    controller = Cluster(name=NAME, address=ADDRESS, channels=channels)
    instruments = {
        "qblox": controller,
        "twpa": SGS100A(address="192.168.0.33", turn_off_on_disconnect=False),
    }
    return Hardware(instruments=instruments, qubits=qubits)
