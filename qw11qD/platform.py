import pathlib

from qibolab.components import AcquireChannel, DcChannel, IqChannel
from qibolab.instruments.qm import Octave, QmChannel, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.parameters import ConfigKinds
from qibolab.platform import Platform
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
    lo_map = {q: f"{q}/drive_lo" for q in ["D1", "D4", "D5"]}
    lo_map["D2"] = lo_map["D3"] = "D2D3/drive_lo"

    twpa_d = SGS100A(name="twpaD", address="192.168.0.33")

    qubits = {}
    for i in range(1, 6):
        q = f"D{i}"
        qubits[q] = Qubit(
            name=q,
            probe=IqChannel(
                name=f"{q}/probe",
                mixer=None,
                lo=f"D/probe_lo",
                acquisition=f"{q}/acquisition",
            ),
            acquisition=AcquireChannel(
                name=f"{q}/acquisition", twpa_pump=twpa_d.name, probe=f"{q}/probe"
            ),
            drive=IqChannel(name=f"{q}/drive", mixer=None, lo=lo_map[q]),
            flux=DcChannel(name=f"{q}/flux"),
        )

    # Connect logical channels to instrument channels (ports)
    # Readout
    channels = [QmChannel(qubit.probe, "octave5", port=1) for qubit in qubits.values()]
    # Acquire
    channels.extend(
        QmChannel(qubit.acquisition, "octave5", port=1) for qubit in qubits.values()
    )
    # Drive
    channels.extend(
        [
            QmChannel(qubits["D1"].drive, "octave5", port=2),
            QmChannel(qubits["D2"].drive, "octave5", port=4),
            QmChannel(qubits["D3"].drive, "octave5", port=5),
            QmChannel(qubits["D4"].drive, "octave6", port=5),
            QmChannel(qubits["D5"].drive, "octave6", port=3),
        ]
    )
    # Flux
    channels.extend(
        QmChannel(qubits[f"D{q}"].flux, "con9", port=q + 2) for q in range(1, 6)
    )

    octaves = {
        "octave5": Octave("octave5", port=104, connectivity="con6"),
        "octave6": Octave("octave6", port=105, connectivity="con8"),
    }
    controller = QmController(
        "qm",
        "192.168.0.101:80",
        octaves=octaves,
        channels=channels,
        calibration_path=FOLDER,
        script_file_name="qua_script.py",
    )
    return Platform.load(path=FOLDER, instruments=[controller, twpa_d], qubits=qubits)
