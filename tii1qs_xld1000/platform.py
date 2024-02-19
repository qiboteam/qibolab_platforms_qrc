import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qm import Octave, OPXplus, QMController
from qibolab.instruments.rohde_schwarz import SGS100A
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
    opx = OPXplus("con1")
    octave = Octave("octave1", port=100, connectivity=opx)
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=[opx],
        octaves=[octave],
        time_of_flight=264,
        calibration_path=FOLDER,
    )
    # twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-31r", port=octave.ports(1))
    # Feedback
    channels |= Channel(name="L2-1", port=octave.ports(1, output=False))
    # Drive
    channels |= Channel(name="L3-31d", port=octave.ports(5))

    # channels |= Channel(name="L99", port=modules["qcm_rf0"].ports("i1", output=False))

    # create qubit objects
    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    instruments = {controller.name: controller}  # , twpa.name: twpa}
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(
        FOLDER.name, qubits, pairs, instruments, settings, resonator_type="3D"
    )
