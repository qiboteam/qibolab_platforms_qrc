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

ADDRESS = "192.168.0.20"
TIME_OF_FLIGHT = 500
FOLDER = pathlib.Path(__file__).parent


def create():
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    runcard = load_runcard(FOLDER)

    # DEBUG: debug folder = report folder
    # import os
    # folder = os.path.dirname(runcard) + "/debug/"
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
    # for name in modules:
    #     modules[name]._debug_folder = folder
    modules = {
        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:2"),
        "qcm_bb1": QcmBb("qcm_bb1", f"{ADDRESS}:4"),
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:6"),
        "qcm_rf1": QcmRf("qcm_rf1", f"{ADDRESS}:8"),
        "qcm_rf2": QcmRf("qcm_rf2", f"{ADDRESS}:10"),
        "qrm_rf_a": QrmRf("qrm_rf_a", f"{ADDRESS}:16"),
        "qrm_rf_b": QrmRf("qrm_rf_b", f"{ADDRESS}:18"),
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    twpa_pump = SGS100A(name="twpa_pump", address="192.168.0.36")

    instruments = {
        controller.name: controller,
        twpa_pump.name: twpa_pump,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-25_a", port=modules["qrm_rf_a"].ports("o1"))
    channels |= Channel(name="L3-25_b", port=modules["qrm_rf_b"].ports("o1"))
    # Feedback
    channels |= Channel(name="L2-5_a", port=modules["qrm_rf_a"].ports("i1", out=False))
    channels |= Channel(name="L2-5_b", port=modules["qrm_rf_b"].ports("i1", out=False))
    # Drive
    channels |= Channel(name="L4-28", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="L3-11", port=modules["qcm_rf0"].ports("o2"))
    channels |= Channel(name="L3-12", port=modules["qcm_rf1"].ports("o1"))
    channels |= Channel(name="L3-13", port=modules["qcm_rf1"].ports("o2"))
    channels |= Channel(name="L4-22", port=modules["qcm_rf2"].ports("o1"))
    # Flux
    channels |= Channel(name="L4-5", port=modules["qcm_bb0"].ports("o1"))
    channels |= Channel(name="L4-1", port=modules["qcm_bb0"].ports("o2"))
    channels |= Channel(name="L4-2", port=modules["qcm_bb0"].ports("o3"))
    channels |= Channel(name="L4-3", port=modules["qcm_bb0"].ports("o4"))
    channels |= Channel(name="L4-4", port=modules["qcm_bb1"].ports("o1"))
    # TWPA
    channels |= Channel(name="L2-22", port=None)
    channels["L2-22"].local_oscillator = twpa_pump

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # remove witness qubit
    # del qubits[5]
    # assign channels to qubits
    for q in [0, 1]:
        qubits[q].readout = channels["L3-25_a"]
        qubits[q].feedback = channels["L2-5_a"]
        qubits[q].twpa = channels["L2-22"]
    for q in [2, 3, 4]:
        qubits[q].readout = channels["L3-25_b"]
        qubits[q].feedback = channels["L2-5_b"]
        qubits[q].twpa = channels["L2-22"]

    qubits[0].drive = channels["L4-28"]
    qubits[0].flux = channels["L4-5"]
    channels["L4-5"].qubit = qubits[0]

    qubits[4].drive = channels["L4-22"]
    qubits[4].flux = channels["L4-4"]
    channels["L4-4"].qubit = qubits[4]
    for q in range(1, 4):
        qubits[q].drive = channels[f"L3-{10 + q}"]
        qubits[q].flux = channels[f"L4-{q}"]
        channels[f"L4-{q}"].qubit = qubits[q]

    # set maximum allowed bias
    for q in range(5):
        qubits[q].flux.max_bias = 2.5

    settings = load_settings(runcard)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
