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
    Line A (6 qubits) is NOT calibrated because signal is very noisy at low readout power.
    We could not calibrate the TWPA neither with QM nor with VNA.
    Line B (5 qubits): calibrated with TWAP and latest status in:
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/151
    Line D (5 qubits): calibrated with TWPA and latest status in:
    https://github.com/qiboteam/qibolab_platforms_qrc/pull/149
    """
    opxs = {i: OPXplus(f"con{i}") for i in range(2, 10)}
    octave_to_opx = {2: 2, 3: 3, 4: 5, 5: 6, 6: 8}
    octaves = {
        i: Octave(f"octave{i}", port=99 + i, connectivity=opxs[octave_to_opx[i]])
        for i in range(2, 7)
    }
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=list(opxs.values()),
        octaves=list(octaves.values()),
        time_of_flight=224,
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    twpa_b = SGS100A(name="twpaB", address="192.168.0.34")
    twpa_d = SGS100A(name="twpaD", address="192.168.0.33")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="readoutA", port=octaves[4].ports(1))
    channels |= Channel(name="readoutB", port=octaves[2].ports(1))
    channels |= Channel(name="readoutD", port=octaves[5].ports(1))
    # Feedback
    channels |= Channel(name="feedbackA", port=octaves[4].ports(1, output=False))
    channels |= Channel(name="feedbackB", port=octaves[2].ports(1, output=False))
    channels |= Channel(name="feedbackD", port=octaves[5].ports(1, output=False))
    # TWPA
    channels |= Channel(name="twpaB", port=None)
    channels["twpaB"].local_oscillator = twpa_b
    channels |= Channel(name="twpaD", port=None)
    channels["twpaD"].local_oscillator = twpa_d
    # Drive
    channels |= Channel(name=f"driveA1", port=octaves[4].ports(2))
    channels |= Channel(name=f"driveA2", port=octaves[4].ports(4))
    channels |= Channel(name=f"driveA3", port=octaves[4].ports(5))
    channels |= Channel(name=f"driveA4", port=octaves[4].ports(3))
    channels |= Channel(name=f"driveA5", port=octaves[6].ports(2))
    channels |= Channel(name=f"driveA6", port=octaves[6].ports(4))
    channels |= Channel(name=f"driveB1", port=octaves[2].ports(2))
    channels |= Channel(name=f"driveB2", port=octaves[2].ports(4))
    channels |= Channel(name=f"driveB3", port=octaves[3].ports(1))
    channels |= Channel(name=f"driveB4", port=octaves[3].ports(4))
    channels |= Channel(name=f"driveB5", port=octaves[3].ports(3))
    channels |= Channel(name=f"driveD1", port=octaves[5].ports(2))
    channels |= Channel(name=f"driveD2", port=octaves[5].ports(4))
    channels |= Channel(name=f"driveD3", port=octaves[5].ports(5))
    channels |= Channel(name=f"driveD4", port=octaves[6].ports(5))
    channels |= Channel(name=f"driveD5", port=octaves[6].ports(3))
    # Flux
    for q in range(1, 6):
        channels |= Channel(name=f"fluxA{q}", port=opxs[7].ports(q + 2))
        channels |= Channel(name=f"fluxB{q}", port=opxs[4].ports(q))
        channels |= Channel(name=f"fluxD{q}", port=opxs[9].ports(q + 2))
    channels |= Channel(name=f"fluxA6", port=opxs[3].ports(8))

    # create qubit objects
    runcard = load_runcard(FOLDER)
    # kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)  # , kernels)

    for q, qubit in qubits.items():
        if "A" in q:
            qubit.readout = channels["readoutA"]
            qubit.feedback = channels["feedbackA"]
            # qubit.twpa = channels["twpaA"]
        elif "B" in q:
            qubit.readout = channels["readoutB"]
            qubit.feedback = channels["feedbackB"]
            qubit.twpa = channels["twpaB"]
        else:
            qubit.readout = channels["readoutD"]
            qubit.feedback = channels["feedbackD"]
            qubit.twpa = channels["twpaD"]
        qubit.drive = channels[f"drive{q}"]
        qubit.flux = channels[f"flux{q}"]

    instruments = {
        controller.name: controller,
        twpa_b.name: twpa_b,
        twpa_d.name: twpa_d,
    }
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)

    settings = load_settings(runcard)
    return Platform(FOLDER.name, qubits, pairs, instruments, settings)
