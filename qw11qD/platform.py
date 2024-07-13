import pathlib

from qibolab.components import (
    AcquireChannel,
    DcChannel,
    IqChannel,
    IqConfig,
    OscillatorConfig,
)
from qibolab.instruments.qm import (
    Octave,
    OpxDcConfig,
    QmAcquisitionConfig,
    QmChannel,
    QmController,
)
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.kernels import Kernels
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent


def create():
    """Lines A and D of QuantWare 21q-chip controlled with Quantum Machines.

    Current status (check before using):
    Line A (6 qubits) is NOT calibrated because signal is very noisy at low readout power,
    possibly due to not using the TWPA pump.
    Line D (5 qubits): calibrated with TWPA and latest status in:
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/149
    """
    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    lo_map = {q: f"drive{q}_lo" for q in ["D1", "D4", "D5"]}
    lo_map["D2"] = lo_map["D3"] = "driveD2D3_lo"

    components = runcard["components"]
    configs = {
        "twpaD": OscillatorConfig(**components["twpaD"]),
        "readoutD_lo": OscillatorConfig(**components["readoutD_lo"]),
    }
    configs |= {n: OscillatorConfig(**components[n]) for n in set(lo_map.values())}

    twpa_d = SGS100A(name="twpaD", address="192.168.0.33")

    # Create logical channels and assign to qubits
    for q, qubit in qubits.items():
        qubit.measure = IqChannel(
            f"readout{q}", mixer=None, lo="readoutD_lo", acquisition=f"acquire{q}"
        )
        # TODO: twpa_pump -> twpa
        qubit.acquisition = AcquireChannel(
            f"acquire{q}", twpa_pump=twpa_d.name, measure=f"readout{q}"
        )
        qubit.drive = IqChannel(f"drive{q}", mixer=None, lo=lo_map[q])
        qubit.flux = DcChannel(f"flux{q}")

        configs[f"readout{q}"] = IqConfig(**components[f"readout{q}"])
        configs[f"acquire{q}"] = QmAcquisitionConfig(**components["acquireD"])
        configs[f"drive{q}"] = IqConfig(**components[f"drive{q}"])
        configs[f"flux{q}"] = OpxDcConfig(**components[f"flux{q}"])

    # Connect logical channels to instrument channels (ports)
    # Readout
    channels = [
        QmChannel(qubit.measure, "octave5", port=1) for qubit in qubits.values()
    ]
    # Acquire
    channels.extend(
        QmChannel(qubit.acquisition, "octave5", port=1, output=False)
        for qubit in qubits.values()
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
        # TODO: Maybe do the conversion below internally in the driver
        # but do we really need this conversion?
        channels={channel.logical_channel.name: channel for channel in channels},
        calibration_path=FOLDER,
        script_file_name="qua_script.py",
    )
    instruments = {
        controller.name: controller,
        twpa_d.name: twpa_d,
    }
    instruments = load_instrument_settings(runcard, instruments)
    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, configs, instruments, settings)
