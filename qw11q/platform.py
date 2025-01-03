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
    """Line D of QuantWare 21q-chip controlled with Quantum Machines.

    Qubits D1, D2, D3 have been tested to work.
    """
    qubits = {
        f"D{i}": Qubit.default(f"D{i}", drive_qudits={(1, 2): f"D{i}/drive12"})
        for i in range(1, 6)
    }
    # Create channels and connect to instrument ports
    # Readout
    channels = {}
    for q in qubits.values():
        assert q.probe is not None
        channels[q.probe] = IqChannel(
            device="octave5", path="1", mixer=None, lo="D/probe_lo"
        )

    # Acquire
    for q in qubits.values():
        assert q.acquisition is not None
        channels[q.acquisition] = AcquisitionChannel(
            device="octave5", path="1", twpa_pump="twpaD", probe=q.probe
        )

    # Drive
    def define_drive(q: str, device: str, port: int, lo: str, transition=None):
        if transition is not None:
            drive = qubits[q].drive_qudits[transition]
        else:
            drive = qubits[q].drive
        assert drive is not None
        channels[drive] = IqChannel(device=device, path=str(port), mixer=None, lo=lo)

    define_drive("D1", "octave5", 2, "D1/drive_lo")
    define_drive("D2", "octave5", 4, "D2D3/drive_lo")
    define_drive("D3", "octave5", 5, "D2D3/drive_lo")
    define_drive("D4", "octave6", 5, "D4/drive_lo")
    define_drive("D5", "octave6", 3, "D5/drive_lo")

    # define drive channles for 12 transition
    define_drive("D1", "octave5", 2, "D1/drive_lo", transition=(1, 2))
    define_drive("D2", "octave5", 4, "D2D3/drive_lo", transition=(1, 2))
    define_drive("D3", "octave5", 5, "D2D3/drive_lo", transition=(1, 2))
    define_drive("D4", "octave6", 5, "D4/drive_lo", transition=(1, 2))
    define_drive("D5", "octave6", 3, "D5/drive_lo", transition=(1, 2))

    # Flux
    for q in range(1, 6):
        qubit = qubits[f"D{q}"]
        assert qubit.flux is not None
        channels[qubit.flux] = DcChannel(device="con9", path=str(q + 2))

    octaves = {
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
    instruments = {"qm": controller, "twpaD": SGS100A(address="192.168.0.33")}
    return Platform.load(path=FOLDER, instruments=instruments, qubits=qubits)
