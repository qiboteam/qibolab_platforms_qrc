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
    opxs = [OPXplus("con5")]
    octave4 = Octave("octave4", port=103, connectivity=opxs[0])
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=opxs,
        octaves=[octave4],
        time_of_flight=224,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    #twpa = SGS100A(name="twpa", address="192.168.0.38")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readout", port=octave4.ports(1))
    # Feedback
    channels |= Channel(name="feedback", port=octave4.ports(1, output=False))
    # Drive
    channels |= Channel(name=f"drive0", port=octave4.ports(4))

    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    for q, qubit in qubits.items():
        qubit.readout = channels["readout"]
        qubit.feedback = channels["feedback"]
        qubit.drive = channels[f"drive{q}"]

    instruments = {controller.name: controller}
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, instruments, settings)
