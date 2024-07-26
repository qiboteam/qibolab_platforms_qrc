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
    """QuantWare 5q-chip controlled using QM.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    opxs = [OPXplus("con2"), OPXplus("con3"), OPXplus("con4")]
    octave2 = Octave("octave2", port=101, connectivity=opxs[0])
    octave3 = Octave("octave3", port=102, connectivity=opxs[1])
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=opxs,
        octaves=[octave2, octave3],
        time_of_flight=224,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    twpa = SGS100A(name="twpa", address="192.168.0.38")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readout", port=octave3.ports(1))
    # Feedback
    channels |= Channel(name="feedback", port=octave3.ports(1, output=False))
    # Drive
    channels |= Channel(name=f"drive0", port=octave2.ports(3))
    channels |= Channel(name=f"drive1", port=octave2.ports(2))
    channels |= Channel(name=f"drive2", port=octave2.ports(1))
    channels |= Channel(name=f"drive3", port=octave2.ports(4))
    channels |= Channel(name=f"drive4", port=octave2.ports(5))
    # Flux
    for q in range(5):
        channels |= Channel(name=f"flux{q}", port=opxs[2].ports(q + 1))
    # TWPA
    channels |= Channel(name="twpa", port=None)
    channels["twpa"].local_oscillator = twpa

    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    for q, qubit in qubits.items():
        qubit.readout = channels["readout"]
        qubit.feedback = channels["feedback"]
        qubit.drive = channels[f"drive{q}"]
        qubit.flux = channels[f"flux{q}"]
        qubit.twpa = channels["twpa"]

    instruments = {controller.name: controller, twpa.name: twpa}
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, instruments, settings)
