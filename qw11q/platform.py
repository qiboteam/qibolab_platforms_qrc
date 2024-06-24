import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qm import Octave, OPXplus, QMController
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
    Line D (5 qubits): is calibrated (also without TWPA pump) up to the details provided in
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/144#issuecomment-2182658507
    """
    opxs = [
        OPXplus("con5"),
        OPXplus("con6"),
        OPXplus("con8"),
        OPXplus("con7"),
        OPXplus("con9"),
    ]
    octaves = [
        Octave("octave4", port=103, connectivity=opxs[0]),
        Octave("octave5", port=104, connectivity=opxs[1]),
        Octave("octave6", port=105, connectivity=opxs[2]),
    ]
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=opxs,
        octaves=octaves,
        time_of_flight=224,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    twpa_a = SGS100A(name="twpaA", address="192.168.0.34")
    twpa_d = SGS100A(name="twpaD", address="192.168.0.33")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readoutA", port=octaves[0].ports(1))
    channels |= Channel(name="readoutD", port=octaves[1].ports(1))
    # Feedback
    channels |= Channel(name="feedbackA", port=octaves[0].ports(1, output=False))
    channels |= Channel(name="feedbackD", port=octaves[1].ports(1, output=False))
    # TWPA
    channels |= Channel(name="twpaA", port=None)
    channels["twpaA"].local_oscillator = twpa_a
    channels |= Channel(name="twpaD", port=None)
    channels["twpaD"].local_oscillator = twpa_d
    # Drive
    channels |= Channel(name=f"driveA1", port=octaves[0].ports(2))
    channels |= Channel(name=f"driveA2", port=octaves[0].ports(4))
    channels |= Channel(name=f"driveA3", port=octaves[0].ports(5))
    channels |= Channel(name=f"driveA4", port=octaves[0].ports(3))
    channels |= Channel(name=f"driveA5", port=octaves[2].ports(2))
    channels |= Channel(name=f"driveA6", port=octaves[2].ports(4))
    channels |= Channel(name=f"driveD1", port=octaves[1].ports(2))
    channels |= Channel(name=f"driveD2", port=octaves[1].ports(4))
    channels |= Channel(name=f"driveD3", port=octaves[1].ports(5))
    channels |= Channel(name=f"driveD4", port=octaves[2].ports(5))
    channels |= Channel(name=f"driveD5", port=octaves[2].ports(3))
    # Flux
    for q in range(1, 6):
        channels |= Channel(name=f"fluxA{q}", port=opxs[3].ports(q + 2))
        channels |= Channel(name=f"fluxD{q}", port=opxs[4].ports(q + 2))
    channels |= Channel(name=f"fluxA6", port=opxs[3].ports(8))

    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    for q, qubit in qubits.items():
        if "A" in q:
            qubit.readout = channels["readoutA"]
            qubit.feedback = channels["feedbackA"]
            qubit.twpa = channels["twpaA"]
        else:
            qubit.readout = channels["readoutD"]
            qubit.feedback = channels["feedbackD"]
            qubit.twpa = channels["twpaD"]
        qubit.drive = channels[f"drive{q}"]
        qubit.flux = channels[f"flux{q}"]

    instruments = {
        controller.name: controller,
        # twpa_a.name: twpa_a,
        # twpa_d.name: twpa_d,
    }
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, instruments, settings)
