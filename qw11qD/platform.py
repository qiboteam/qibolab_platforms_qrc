import pathlib
from typing import cast

from qibolab.components import AcquireChannel, Channel, DcChannel, IqChannel
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.identifier import ChannelId
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

    qubits = {
        f"D{i}": Qubit(
            drive=f"D{i}/drive",
            flux=f"D{i}/flux",
            probe=f"D{i}/probe",
            acquisition=f"D{i}/acquisition",
        )
        for i in range(1, 6)
    }

    # Connect logical channels to instrument channels (ports)
    # Readout
    channels = {
        q.probe: IqChannel(device="octave5", path="1", mixer=None, lo="D/probe_lo")
        for q in qubits.values()
    }
    # Acquire
    channels |= {
        q.acquisition: AcquireChannel(
            device="octave5", path="1", twpa_pump=twpa_d.name, probe=q.probe
        )
        for q in qubits.values()
    }
    # Drive
    channels |= {
        qubits["D1"].drive: IqChannel(
            device="octave5", path="2", mixer=None, lo=lo_map["D1"]
        ),
        qubits["D2"].drive: IqChannel(
            device="octave5", path="4", mixer=None, lo=lo_map["D2"]
        ),
        qubits["D3"].drive: IqChannel(
            device="octave5", path="5", mixer=None, lo=lo_map["D3"]
        ),
        qubits["D4"].drive: IqChannel(
            device="octave6", path="5", mixer=None, lo=lo_map["D4"]
        ),
        qubits["D5"].drive: IqChannel(
            device="octave6", path="3", mixer=None, lo=lo_map["D5"]
        ),
    }
    # Flux
    channels |= {
        qubits[f"D{q}"].flux: DcChannel(device="con9", path=str(q + 2))
        for q in range(1, 6)
    }
    channels = cast(dict[ChannelId, Channel], channels)

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
