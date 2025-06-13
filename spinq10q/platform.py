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

NAME = "spinq10q610_qblox"
ADDRESS = "192.168.0.6"
FOLDER = pathlib.Path(__file__).parent


def create():
    """SpinQ 10q-chip qubits 6 - 10 controlled using qblox cluster 6.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:20"),  # RO: 6, 7, 8, 9, 10
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:8"),  # Drive: 6
        "qcm_rf1": QcmRf("qcm_rf1", f"{ADDRESS}:10"),  # Drive: 7, 8
        "qcm_rf2": QcmRf("qcm_rf2", f"{ADDRESS}:12"),  # Drive: 9, 10
        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:4"),  # Flux: 6, 7, 8
        "qcm_bb1": QcmBb("qcm_bb1", f"{ADDRESS}:6"),  # Flux: 9, 10
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.39")

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }

    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    channels = ChannelMap()

    # Readout
    channels |= Channel(
        name="L3-21", port=modules["qrm_rf0"].ports("o1")
    )  # 6, 7, 8, 9, 10

    # Feedback
    channels |= Channel(
        name="L2-17", port=modules["qrm_rf0"].ports("i1", out=False)
    )  # 6, 7, 8, 9, 10

    # Drive
    channels |= Channel(name="L6-6", port=modules["qcm_rf0"].ports("o2"))  # 6
    channels |= Channel(name="L6-7", port=modules["qcm_rf1"].ports("o1"))  # 7
    channels |= Channel(name="L6-8", port=modules["qcm_rf1"].ports("o2"))  # 8
    channels |= Channel(name="L6-9", port=modules["qcm_rf2"].ports("o1"))  # 9
    channels |= Channel(name="L6-10", port=modules["qcm_rf2"].ports("o2"))  # 10

    # Flux - Qubits
    channels |= Channel(name="L6-44", port=modules["qcm_bb0"].ports("o2"))  # 6
    channels |= Channel(name="L6-45", port=modules["qcm_bb0"].ports("o3"))  # 7
    channels |= Channel(name="L6-46", port=modules["qcm_bb0"].ports("o4"))  # 8
    channels |= Channel(name="L6-47", port=modules["qcm_bb1"].ports("o1"))  # 9
    channels |= Channel(name="L6-48", port=modules["qcm_bb1"].ports("o2"))  # 10

    # TWPA
    channels |= Channel(name="TWPA", port=None)
    channels["TWPA"].local_oscillator = twpa_pump0

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits and sweetspots(operating points)
    for q in range(6, 10):  # q0, q1
        qubits[q].readout = channels["L3-21"]
        qubits[q].feedback = channels["L2-17"]

    for q in range(6, 10):
        qubits[q].drive = channels[f"L6-{q}"]
        qubits[q].flux = channels[f"L6-{38 + q}"]
        qubits[q].twpa = channels["TWPA"]
        channels[f"L6-{38 + q}"].qubit = qubits[q]
        qubits[q].flux.max_bias = 2.5

    settings = load_settings(runcard)

    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="2D",
        couplers=couplers,
    )
