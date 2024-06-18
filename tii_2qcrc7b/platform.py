import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster_qcm_bb import QcmBb
from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "tii_2qcrc7b"
ADDRESS = "192.168.0.2"
FOLDER = pathlib.Path(__file__).parent


def create():
    """"QRC QFoundry 2Q Chip for Cross Resonance Gates"""
    runcard = load_runcard(FOLDER)

    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:2"),  # feedline
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:10"),  # q1, q2
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    channels = ChannelMap()

    # Readout
    channels |= Channel(name="V2", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="W7", port=modules["qrm_rf0"].ports("i1", out=False))
     # Drive
    channels |= Channel(name="W3", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="W4", port=modules["qcm_rf0"].ports("o2"))

    # create qubit objects
    qubits, _, pairs = load_qubits(runcard)

    # assign readout channels to qubits
    for q in range(0, 2):  # q0, q1
        qubits[q].readout = channels["V2"]
        qubits[q].feedback = channels["W7"]

    # assign drive channels to qubits
    for q in range(0, 2):
        qubits[q].drive = channels[f"W{3 + q}"]
        channels[f"W{3 + q}"].qubit = qubits[q]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
