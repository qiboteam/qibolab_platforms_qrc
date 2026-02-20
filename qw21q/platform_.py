import pathlib
from typing import Optional

from qibolab import (
    AcquisitionChannel,
    Channel,
    ConfigKinds,
    DcChannel,
    Hardware,
    IqChannel,
    Qubit,
    QubitMap,
)
from qibolab._core.identifier import ChannelId
from qibolab._core.serialize import Model
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


class Label(Model):
    line: str
    n: int

    @classmethod
    def from_str(cls, label: str) -> "Label":
        return cls(line=label[0], n=int(label[1:]))

    @classmethod
    def from_ch(cls, channel: ChannelId) -> "Label":
        return cls.from_str(channel.split("/")[0])

    def __str__(self) -> str:
        return f"{self.line}{self.n}"


def _qubit(line: str, n: int) -> tuple[str, Qubit]:
    label = Label(line=line, n=n)
    return str(label), Qubit.default(
        str(label), drive_extra={(1, 2): f"{label}/drive12"}
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
    label = Label.from_ch(q.probe)
    line = label.line
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
    label = Label.from_ch(q.drive)
    lo = f"{label}/drive_lo"
    device, port = DRIVES[label.line][label.n]
    return (
        _drive(q, device, port, lo)
        |
        # define drive channles for 12 transition
        _drive(q, device, port, lo, transition=(1, 2))
    )


# flux lines to controller mapping
FLUX = {
    "A": {
        1: ("con7", 6),
        2: ("con7", 7),
        3: ("con7", 8),
        4: ("con7", 9),
        5: ("con7", 10),
        6: ("con9", 9),
    },
    "B": {
        1: ("con4", 1),
        2: ("con4", 2),
        3: ("con4", 3),
        4: ("con4", 4),
        5: ("con4", 5),
    },
    "C": {
        1: ("con4", 6),
        2: ("con4", 7),
        3: ("con4", 8),
        4: ("con4", 9),
        5: ("con4", 10),
    },
    "D": {
        1: ("con7", 1),
        2: ("con7", 2),
        3: ("con7", 3),
        4: ("con7", 4),
        5: ("con7", 5),
    },
}


def _flux(q: Qubit) -> dict[ChannelId, DcChannel]:
    assert q.flux is not None
    label = Label.from_ch(q.flux)
    device, path = FLUX[label.line][label.n]
    return {q.flux: DcChannel(device=device, path=str(path))}


# octaves connections
OCTAVES = {
    "oct1": (11100, "con1"),
    "oct2": (11101, "con2"),
    "oct3": (11102, "con3"),
    "oct4": (11103, "con5"),
    "oct5": (11104, "con6"),
    "oct6": (11105, "con8"),
}


def create() -> Hardware:
    """QuantWare 21q-chip controlled with Quantum Machines."""

    qubits: QubitMap = dict(
        _qubit(line, i) for i in range(1, 6) for line in ("A", "B", "C", "D")
    )
    qubits["A6"] = _qubit("A", 6)[1]

    # Create channels and connect to instrument ports
    channels = {}

    for q in qubits.values():
        channels |= _feedline(q)
        channels |= _drives(q)
        channels |= _flux(q)

    octaves = {
        name: Octave(name, port=port, connectivity=controller)
        for name, (port, controller) in OCTAVES.items()
    }

    controller = QmController(
        address="192.168.0.101:80",
        octaves=octaves,
        channels=channels,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    instruments = {
        "qm": controller,
        "twpaB": SGS100A(address="192.168.0.34", turn_off_on_disconnect=False),
        "twpaD": SGS100A(address="192.168.0.33", turn_off_on_disconnect=False),
    }
    return Hardware(instruments=instruments, qubits=qubits)
