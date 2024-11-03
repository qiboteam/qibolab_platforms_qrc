from collections import defaultdict
import pathlib
from typing import Optional, Union

from qibolab import (
    AcquisitionChannel,
    ConfigKinds,
    Channel,
    DcChannel,
    IqChannel,
    Platform,
    Qubit,
)

from qibolab.instruments.qblox import Cluster, QbloxConfigs
from qibolab._core.platform.platform import QubitMap
from qibolab.instruments.rohde_schwarz import SGS100A

# Register Qblox-specific configurations for parameters loading
ConfigKinds.extend([QbloxConfigs])

FOLDER = pathlib.Path(__file__).parent
ADDRESS = "192.168.0.6"
"""Cluster ``iqm5q_qblox``."""

# the only cluster of the config
CLUSTER = {
    "qrm_rf0": (19, {"io1": ["q0", "q1"]}),
    "qrm_rf1": (20, {"io1": ["q2", "q3", "q4"]}),
    "qcm_rf0": (8, {1: ["q1"], 2: ["q2"]}),
    "qcm_rf1": (10, {1: ["q3"], 2: ["q4"]}),
    "qcm_rf2": (12, {1: ["q0"]}),
    "qcm0": (2, {1: ["q0"], 2: ["q1"], 3: ["q2"], 4: ["q3"]}),
    "qcm1": (4, {1: ["q4"], 2: ["c1"], 4: ["c3"]}),
    "qcm2": (6, {2: ["c4"]}),
    "qcm3": (17, {1: ["c0"]}),
}
"""Connections compact representation."""


def map_ports(cluster: dict, qubits: dict, couplers: Optional[dict] = None) -> dict:
    """Extract channels from compact representation.

    Conventions:
    - each item is a module
    - the first element of each value is the module's slot ID
    - the second element is a map from ports to qubits
        - ports
            - they are `i{n}` or `o{n}` for the inputs and outputs respectively
            - `io{n}` is also allowed, to signal that both are connected (cater for the specific
              case of the QRM_RF where there are only one port of each type)
            - if it's just an integer, it is intended to be an output (equivalent to `o{n}`)
        - values
            - list of element names
            - they are `q{name}` or `c{name}` for qubits and couplers respectively
            - multiple elements are allowed, for multiplexed ports

    .. note::

        integer qubit names are not allowed

    .. todo::

        Currently channel types are inferred from the module type, encoded in its name. At
        least an override should be allowed (per module, per port, per qubit).
    """
    d = {
        "qubits": defaultdict(lambda: defaultdict(dict)),
        "couplers": defaultdict(lambda: defaultdict(dict)),
    }

    if couplers is None:
        couplers = {}

    def type_(el: str):
        return "qubits" if el[0] == "q" else "couplers"

    def chtype_(mod: str, input: bool) -> tuple[str, type[Channel]]:
        if mod.startswith("qcm_rf"):
            return "drive", IqChannel
        if mod.startswith("qcm"):
            return "flux", DcChannel
        if mod.startswith("qrm_rf"):
            if input:
                return "acquisition", AcquisitionChannel
            return "probe", IqChannel
        raise ValueError

    def ch_(mod: str, port: Union[int, str], slot: int) -> dict:
        if isinstance(port, str) and port.startswith("io"):
            return {
                "probe": IqChannel(path=f"{slot}/o{port[2:]}"),
                "acquisition": AcquisitionChannel(path=f"{slot}/o{port[2:]}"),
            }
        port = f"o{port}" if isinstance(port, int) else port
        name, cls = chtype_(mod, port[0] == "i")
        return {name: cls(path=f"{slot}/{port}")}

    for mod, props in cluster.items():
        slot = props[0]
        for port, els in props[1].items():
            for el in els:
                nel = el[1:]
                d[type_(el)][nel] |= ch_(mod, port, slot)

    channels = {}
    for kind, elements in [("qubits", qubits), ("couplers", couplers)]:
        for name, el in elements.items():
            for chname, ch in d[kind][name].items():
                channels[getattr(el, chname)] = ch
            if kind == "qubits":
                channels[el.acquisition] = channels[el.acquisition].model_copy(
                    update={"probe": el.probe}
                )
    return channels


def create():
    """IQM 5q-chip controlled with a Qblox cluster."""
    qubits: QubitMap = {f"q{i}": Qubit.default(f"q{i}") for i in range(5)}
    couplers: QubitMap = {f"c{i}": Qubit.default(f"c{i}") for i in (0, 1, 3, 4)}

    # Create channels and connect to instrument ports
    channels = map_ports(CLUSTER, qubits, couplers)

    # update channel information beyond connections
    for q in qubits.values():
        if q.acquisition is not None:
            channels[q.acquisition] = channels[q.acquisition].model_copy(
                update={"twpa_pump": "twpa"}
            )

    controller = Cluster(address=ADDRESS, channels=channels)
    instruments = {"qblox": controller, "twpa": SGS100A(address="192.168.0.35")}
    return Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, couplers=couplers
    )
