import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qm import FEM, OPX1000, Octave, QMController
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
    """QuantWare 5q-chip controlled with Quantum Machines.

    Current status (check before using):
    Qubits 0 and 2 are calibrated up to single shot.
    Qubit 1 cannot be put at the sweetspot because then Qubit 2 is not working.
    Qubit 3 sweetspot cannot be reach by QM.
    Qubit 4 does not show good Rabi.

    Some reports:
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/147#pullrequestreview-2146505676
    """
    opx = OPX1000("con1", {1: FEM("LF"), 2: FEM("LF"), 4: FEM("LF")})
    octave1 = Octave("octave1", port=250, connectivity=opx.connectivity(1))
    octave2 = Octave("octave2", port=251, connectivity=opx.connectivity(2))
    controller = QMController(
        "qm",
        "192.168.0.102:80",
        opxs=[opx],
        octaves=[octave1, octave2],
        time_of_flight=224,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    twpa = SGS100A(name="twpa", address="192.168.0.38")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readout", port=octave2.ports(1))
    # Feedback
    channels |= Channel(name="feedback", port=octave2.ports(1, output=False))
    # Drive
    channels |= Channel(name="drive0", port=octave1.ports(2))
    channels |= Channel(name="drive1", port=octave1.ports(3))
    channels |= Channel(name="drive2", port=octave1.ports(1))
    channels |= Channel(name="drive3", port=octave1.ports(4))
    channels |= Channel(name="drive4", port=octave2.ports(2))
    # Flux
    channels |= Channel(name="flux0", port=opx.ports(4, 4), max_offset=2.5)
    channels |= Channel(name="flux1", port=opx.ports(4, 1), max_offset=2.5)
    channels |= Channel(name="flux2", port=opx.ports(4, 3), max_offset=2.5)
    channels |= Channel(name="flux3", port=opx.ports(4, 2), max_offset=2.5)
    channels |= Channel(name="flux4", port=opx.ports(4, 5), max_offset=2.5)
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