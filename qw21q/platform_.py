import pathlib
from typing import Optional

from qibolab import (
    AcquisitionChannel,
    Channel,
    ConfigKinds,
    DcChannel,
    IqChannel,
    Platform,
    Qubit,
)
from qibolab._core.identifier import ChannelId
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


def _qubit(line: str, i: int) -> tuple[str, Qubit]:
    label = f"{line}{i}"
    return label, Qubit.default(
        f"{line}{i}", drive_extra={(1, 2): f"{line}{i}/drive12"}
    )


# feedlines to octaves mapping
FEEDLINES = {
    "A": "oct1",
    "B": "oct2",
    "C": "oct3",
    "D": "oct4",
}


def _feedline(q: Qubit, mixer: Optional[str] = None) -> dict[ChannelId, Channel]:
    assert q.probe is not None
    assert q.acquisition is not None
    line = q.probe[0]
    return {
        q.probe: IqChannel(
            device=FEEDLINES[line], path="1", mixer=mixer, lo=f"{line}/probe_lo"
        ),
        q.acquisition: AcquisitionChannel(
            device=FEEDLINES[line], path="1", twpa_pump=f"twpa{line}", probe=q.probe
        ),
    }


# drives to octaves mapping
DRIVES = {
    "A": {
        1: ("oct1", 4),
        2: ("oct1", 2),
        3: ("oct5", 4),
        4: ("oct1", 5),
        5: ("oct1", 3),
        6: ("oct4", 5),
    },
    "B": {
        1: ("oct2", 2),
        2: ("oct2", 4),
        3: ("oct2", 5),
        4: ("oct3", 4),
        5: ("oct3", 3),
    },
    "C": {
        1: ("oct6", 2),
        2: ("oct5", 2),
        3: ("oct5", 3),
        4: ("oct6", 3),
        5: ("oct5", 5),
    },
    "D": {
        1: ("oct2", 3),
        2: ("oct4", 2),
        3: ("oct4", 3),
        4: ("oct4", 4),
        5: ("oct3", 2),
    },
}


def _drive(
    q: Qubit, device: str, port: int, lo: str, transition=None
) -> dict[ChannelId, IqChannel]:
    if transition is not None:
        drive = q.drive_extra[transition]
    else:
        drive = q.drive
    assert drive is not None
    return {drive: IqChannel(device=device, path=str(port), mixer=None, lo=lo)}


def _drives(q: Qubit) -> dict[ChannelId, IqChannel]:
    assert q.drive is not None
    label = q.drive.split("/")[0]
    line = label[0]
    n = int(label[1:])
    lo = f"{label}/drive_lo"
    device, port = DRIVES[line][n]
    return (
        _drive(q, device, port, lo)
        |
        # define drive channles for 12 transition
        _drive(q, device, port, lo, transition=(1, 2))
    )


def create():
    """QuantWare 21q-chip controlled with Quantum Machines."""

    qubits = dict(_qubit(line, i) for i in range(1, 6) for line in ("A", "B", "C", "D"))
    qubits["A6"] = _qubit("A", 6)[1]

    # Create channels and connect to instrument ports
    channels = {}

    for q in qubits.values():
        channels |= _feedline(q)
        channels |= _drives(q)

    return channels
    #
    # # Flux
    # for q in range(1, 6):
    #     qubit = qubits[f"B{q}"]
    #     assert qubit.flux is not None
    #     channels[qubit.flux] = DcChannel(device="con4", path=str(q))
    #
    # octaves = {
    #     "oct2": Octave("oct2", port=11101, connectivity="con2"),
    #     "oct3": Octave("oct3", port=11102, connectivity="con3"),
    # }
    # controller = QmController(
    #     address="192.168.0.101:80",
    #     octaves=octaves,
    #     channels=channels,
    #     calibration_path=FOLDER,
    #     script_file_name="qua_script.py",
    # )
    # instruments = {
    #     "qm": controller,
    #     "twpaB": SGS100A(address="192.168.0.34"),
    # }
    # return Platform.load(path=FOLDER, instruments=instruments, qubits=qubits)
