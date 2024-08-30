import pathlib

from qibolab.components import AcquireChannel, Channel, DcChannel, IqChannel
from qibolab.identifier import ChannelId
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.parameters import ConfigKinds
from qibolab.platform import Platform
from qibolab.platform.platform import QubitMap
from qibolab.qubits import Qubit

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


def create():
    """Lines A and D of QuantWare 21q-chip controlled with Quantum Machines.

    Current status (check before using): Line A (6 qubits) is NOT
    calibrated because signal is very noisy at low readout power,
    possibly due to not using the TWPA pump. Line D (5 qubits):
    calibrated with TWPA and latest status in:
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/149
    """
    twpa_d = SGS100A(name="twpaD", address="192.168.0.33")

    qubits: QubitMap = {
        f"D{i}": Qubit(
            drive=f"D{i}/drive",
            flux=f"D{i}/flux",
            probe=f"D{i}/probe",
            acquisition=f"D{i}/acquisition",
        )
        for i in range(1, 6)
    }
    for q in qubits.values():
        assert q.probe is not None

    # Create channels and connect to instrument ports
    # Readout
    channels: dict[ChannelId, Channel] = {}
    for q in qubits.values():
        assert q.probe is not None
        channels[q.probe] = IqChannel(
            device="octave5", path="1", mixer=None, lo="D/probe_lo"
        )

    # Acquire
    for q in qubits.values():
        assert q.acquisition is not None
        channels[q.acquisition] = AcquireChannel(
            device="octave5", path="1", twpa_pump=twpa_d.name, probe=q.probe
        )

    # Drive
    def define_drive(q: str, device: str, port: int, lo: str):
        drive = qubits[q].drive
        assert drive is not None
        channels[drive] = IqChannel(device=device, path=str(port), mixer=None, lo=lo)

    define_drive("D1", "octave5", 2, "D1/drive_lo")
    define_drive("D2", "octave5", 4, "D2D3/drive_lo")
    define_drive("D3", "octave5", 5, "D2D3/drive_lo")
    define_drive("D4", "octave6", 5, "D4/drive_lo")
    define_drive("D5", "octave6", 3, "D5/drive_lo")

    # Flux
    for q in range(1, 6):
        qubit = qubits[f"D{q}"]
        assert qubit.flux is not None
        channels[qubit.flux] = DcChannel(device="con9", path=str(q + 2))

    octaves = {
        "octave5": Octave("octave5", port=104, connectivity="con6"),
        "octave6": Octave("octave6", port=105, connectivity="con8"),
    }
    controller = QmController(
        name="qm",
        address="192.168.0.101:80",
        octaves=octaves,
        channels=channels,
        calibration_path=FOLDER,
        script_file_name="qua_script.py",
    )
    return Platform.load(path=FOLDER, instruments=[controller, twpa_d], qubits=qubits)
