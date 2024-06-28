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

NAME = "iqm5q_qblox"
ADDRESS = "192.168.0.6"
FOLDER = pathlib.Path(__file__).parent


def create():
    """IQM 5q-chip controlled using qblox cluster 6.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:19"),  # RO: q0, q1
        "qrm_rf1": QrmRf("qrm_rf1", f"{ADDRESS}:20"),  # RO: q2, q3, q4
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:8"),  # Drive: q1, q2
        "qcm_rf1": QcmRf("qcm_rf1", f"{ADDRESS}:10"),  # Drive: q3, q4
        "qcm_rf2": QcmRf("qcm_rf2", f"{ADDRESS}:12"),  # Drive: q0
        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:2"),  # Flux: q0, q1, q2, q3
        "qcm_bb1": QcmBb("qcm_bb1", f"{ADDRESS}:4"),  # Flux/Coupler: q4, c1, c3
        "qcm_bb2": QcmBb("qcm_bb2", f"{ADDRESS}:6"),  # Flux/Coupler: c4
        "qcm_bb3": QcmBb("qcm_bb3", f"{ADDRESS}:17"),  # Flux/Coupler: c0
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.35")

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }

    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    channels = ChannelMap()

    # Readout
    channels |= Channel(name="L3-31a", port=modules["qrm_rf0"].ports("o1"))  # q0, q1
    channels |= Channel(
        name="L3-31b", port=modules["qrm_rf1"].ports("o1")
    )  # q2, q3, q4
    # Feedback
    channels |= Channel(
        name="L2-7a", port=modules["qrm_rf0"].ports("i1", out=False)
    )  # q0, q1
    channels |= Channel(
        name="L2-7b", port=modules["qrm_rf1"].ports("i1", out=False)
    )  # q2, q3, q4
    # Drive
    channels |= Channel(name="L4-16", port=modules["qcm_rf0"].ports("o1"))  # q1
    channels |= Channel(name="L4-17", port=modules["qcm_rf0"].ports("o2"))  # q2
    channels |= Channel(name="L4-18", port=modules["qcm_rf1"].ports("o1"))  # q3
    channels |= Channel(name="L4-19", port=modules["qcm_rf1"].ports("o2"))  # q4
    channels |= Channel(name="L4-15", port=modules["qcm_rf2"].ports("o1"))  # q0

    # Flux - Qubits
    channels |= Channel(name="L4-6", port=modules["qcm_bb0"].ports("o1"))  # q0
    channels |= Channel(name="L4-7", port=modules["qcm_bb0"].ports("o2"))  # q1
    channels |= Channel(name="L4-8", port=modules["qcm_bb0"].ports("o3"))  # q2
    channels |= Channel(name="L4-9", port=modules["qcm_bb0"].ports("o4"))  # q3
    channels |= Channel(name="L4-10", port=modules["qcm_bb1"].ports("o1"))  # q4

    # Flux - Couplers
    channels |= Channel(name="L4-12", port=modules["qcm_bb1"].ports("o2"))  # c1
    channels |= Channel(name="L4-13", port=modules["qcm_bb1"].ports("o4"))  # c3
    channels |= Channel(name="L4-14", port=modules["qcm_bb2"].ports("o2"))  # c4
    channels |= Channel(name="L4-5", port=modules["qcm_bb3"].ports("o1"))  # c0

    # TWPA
    channels |= Channel(name="L3-32", port=None)
    channels["L3-32"].local_oscillator = twpa_pump0

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits and sweetspots(operating points)
    for q in range(0, 2):  # q0, q1
        qubits[q].readout = channels["L3-31a"]
        qubits[q].feedback = channels["L2-7a"]
    for q in range(2, 5):  # q2, q3, q4
        qubits[q].readout = channels["L3-31b"]
        qubits[q].feedback = channels["L2-7b"]

    for q in range(0, 5):
        qubits[q].drive = channels[f"L4-{15 + q}"]
        qubits[q].flux = channels[f"L4-{6 + q}"]
        qubits[q].twpa = channels["L3-32"]
        channels[f"L4-{6 + q}"].qubit = qubits[q]
        qubits[q].flux.max_bias = 2.5

    for i, coupler in enumerate(couplers):
        couplers[coupler].flux = (
            channels[f"L4-{11 + i}"] if i > 0 else channels[f"L4-5"]
        )
        couplers[coupler].flux.max_bias = 2.5

    settings = load_settings(runcard)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
