import pathlib

from qibolab import (
    AcquisitionChannel,
    Channel,
    ConfigKinds,
    DcChannel,
    IqChannel,
    Platform,
    Qubit,
)
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


def create():
    """Lines B and D of QuantWare 21q-chip controlled with Quantum Machines.

    Qubits D1, D2, D3 have been tested to work.
    """
    qubits = {
        f"B{i}": Qubit.default(f"B{i}", drive_extra={(1, 2): f"B{i}/drive12"})
        for i in range(1, 6)
    } | {
        f"D{i}": Qubit.default(f"D{i}", drive_extra={(1, 2): f"D{i}/drive12"})
        for i in range(1, 6)
    }
    # Create channels and connect to instrument ports
    channels = {}
    for i in range(1, 6):
        q = qubits[f"B{i}"]
        assert q.probe is not None
        assert q.acquisition is not None
        channels[q.probe] = IqChannel(
            device="octave2", path="1", mixer=None, lo="B/probe_lo"
        )
        channels[q.acquisition] = AcquisitionChannel(
            device="octave2", path="1", twpa_pump="twpaB", probe=q.probe
        )

        q = qubits[f"D{i}"]
        assert q.probe is not None
        assert q.acquisition is not None
        channels[q.probe] = IqChannel(
            device="octave6", path="1", mixer=None, lo="D/probe_lo"
        )
        channels[q.acquisition] = AcquisitionChannel(
            device="octave6", path="1", twpa_pump="twpaD", probe=q.probe
        )

    # Drive
    def define_drive(q: str, device: str, port: int, lo: str, transition=None):
        if transition is not None:
            drive = qubits[q].drive_extra[transition]
        else:
            drive = qubits[q].drive
        assert drive is not None
        channels[drive] = IqChannel(device=device, path=str(port), mixer=None, lo=lo)

    def define_transitions(q: str, device: str, port: int, lo: str):
        define_drive(q, device, port, lo)
        # define drive channles for 12 transition
        define_drive(q, device, port, lo, transition=(1, 2))

    define_transitions("B1", "octave2", 2, "B1/drive_lo")
    define_transitions("B2", "octave2", 4, "B2/drive_lo")
    define_transitions("B3", "octave3", 1, "B3/drive_lo")
    define_transitions("B4", "octave3", 4, "B4/drive_lo")
    define_transitions("B5", "octave3", 3, "B5/drive_lo")

    define_transitions("D1", "octave5", 2, "D1/drive_lo")
    define_transitions("D2", "octave5", 4, "D2D3/drive_lo")
    define_transitions("D3", "octave5", 5, "D2D3/drive_lo")
    define_transitions("D4", "octave6", 5, "A6D4/drive_lo")
    define_transitions("D5", "octave6", 3, "A5D5/drive_lo")

    # Flux
    for q in range(1, 6):
        qubit = qubits[f"B{q}"]
        assert qubit.flux is not None
        channels[qubit.flux] = DcChannel(device="con4", path=str(q))

        qubit = qubits[f"D{q}"]
        assert qubit.flux is not None
        channels[qubit.flux] = DcChannel(device="con9", path=str(q + 2))

    octaves = {
        "octave2": Octave("octave2", port=11101, connectivity="con2"),
        "octave3": Octave("octave3", port=11102, connectivity="con3"),
        "octave5": Octave("octave5", port=11104, connectivity="con6"),
        "octave6": Octave("octave6", port=11105, connectivity="con8"),
    }
    controller = QmController(
        address="192.168.0.101:80",
        octaves=octaves,
        channels=channels,
        calibration_path=FOLDER,
        script_file_name="qua_script.py",
    )
    instruments = {
        "qm": controller,
        "twpaB": SGS100A(address="192.168.0.34"),
        "twpaD": SGS100A(address="192.168.0.33"),
    }
    return Platform.load(path=FOLDER, instruments=instruments, qubits=qubits)
