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

NAME = "spinq10q_qblox"
ADDRESS = "192.168.0.6"
FOLDER = pathlib.Path(__file__).parent


def create():
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:18"),
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:8"),
        "qcm_rf1": QcmRf("qcm_rf1", f"{ADDRESS}:10"),
        "qcm_rf2": QcmRf("qcm_rf2", f"{ADDRESS}:12"),
        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:2"),
        "qcm_bb1": QcmBb("qcm_bb1", f"{ADDRESS}:4"),
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }
    instruments.update(modules)
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-20", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="L1-1", port=modules["qrm_rf0"].ports("i1", out=False))
    # Drive
    channels |= Channel(name="L6-1", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="L6-2", port=modules["qcm_rf0"].ports("o2"))
    channels |= Channel(name="L6-3", port=modules["qcm_rf1"].ports("o1"))
    channels |= Channel(name="L6-4", port=modules["qcm_rf1"].ports("o2"))
    channels |= Channel(name="L6-5", port=modules["qcm_rf2"].ports("o1"))
    # Flux
    channels |= Channel(name="L6-39", port=modules["qcm_bb0"].ports("o1"))
    channels |= Channel(name="L6-40", port=modules["qcm_bb0"].ports("o2"))
    channels |= Channel(name="L6-41", port=modules["qcm_bb0"].ports("o3"))
    channels |= Channel(name="L6-42", port=modules["qcm_bb0"].ports("o4"))
    channels |= Channel(name="L6-43", port=modules["qcm_bb1"].ports("o1"))
    # TWPA
    channels |= Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump0

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    for q in [1, 2, 3, 4, 5]:
        qubits[q].readout = channels["L3-20"]
        qubits[q].feedback = channels["L1-1"]
        qubits[q].twpa = channels["L3-10"]
        qubits[q].drive = channels[f"L6-{q}"]
        qubits[q].flux = channels[f"L6-{38+q}"]
        channels[f"L6-{38+q}"].qubit = qubits[q]
        qubits[q].flux.max_bias = 2.5

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
