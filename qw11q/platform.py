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
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    opxs = [OPXplus("con5"), OPXplus("con6"), OPXplus("con8"), OPXplus("con7"), OPXplus("con9")]
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
    # TODO: Add TWPA pumps
    #twpa = SGS100A(name="twpa", address="192.168.0.38")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readoutA", port=octaves[0].ports(1))
    channels |= Channel(name="readoutD", port=octaves[1].ports(1))
    # Feedback
    channels |= Channel(name="feedbackA", port=octaves[0].ports(1, output=False))
    channels |= Channel(name="feedbackD", port=octaves[1].ports(1, output=False))
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

    # TWPA
    #channels |= Channel(name="twpa", port=None)
    #channels["twpa"].local_oscillator = twpa

    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    for q, qubit in qubits.items():
        if "A" in q:
            qubit.readout = channels["readoutA"]
            qubit.feedback = channels["feedbackA"]
        else:
            qubit.readout = channels["readoutD"]
            qubit.feedback = channels["feedbackD"]
        qubit.drive = channels[f"drive{q}"]
        qubit.flux = channels[f"flux{q}"]
        # qubit.twpa = channels["twpa"]

    instruments = {controller.name: controller} # , twpa.name: twpa}
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, instruments, settings)
