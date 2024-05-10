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


QPU_NAME = "spinq10q"
ADDRESS = "192.168.0.6"
FOLDER = pathlib.Path(__file__).parent


def create():
    """SpinQ 10Q controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER) #Load parameters
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:20"), # qubits q1, q2, q3, q4, q5

        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:8"), #q1, q2
        "qcm_rf1": QcmRf("qcm_rf1", f"{ADDRESS}:10"),
        "qcm_rf2": QcmRf("qcm_rf2", f"{ADDRESS}:12"),

        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:2"), # qubits q1, q2, q3, q4
        "qcm_bb1": QcmBb("qcm_bb1", f"{ADDRESS}:4"), # qubits q5, q6, q7, q8
    }

    # modules["qrm_rf0"]._execution_time = 30

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")



    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }

    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-20", port=modules["qrm_rf0"].ports("o1"))
    
    # Feedback
    channels |= Channel(name="L1-1",  port=modules["qrm_rf0"].ports("i1", out=False))

    # Drive
    channels |= Channel(name="L6-1", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="L6-2", port=modules["qcm_rf0"].ports("o2"))
    channels |= Channel(name="L6-3", port=modules["qcm_rf1"].ports("o1"))
    channels |= Channel(name="L6-4", port=modules["qcm_rf1"].ports("o2"))
    channels |= Channel(name="L6-5", port=modules["qcm_rf2"].ports("o1"))

    channels |= Channel(name="L6-6", port=modules["qcm_rf2"].ports("o2"))
    
    # channels |= Channel(name="L6-7", port=modules["qcm_rf3"].ports("o1"))
    # channels |= Channel(name="L6-8", port=modules["qcm_rf3"].ports("o2"))
    # channels |= Channel(name="L6-9", port=modules["qcm_rf4"].ports("o1"))
    # channels |= Channel(name="L6-10", port=modules["qcm_rf4"].ports("o2"))

    # Flux
    channels |= Channel(name="L6-39", port=modules["qcm_bb0"].ports("o1"))
    channels |= Channel(name="L6-40", port=modules["qcm_bb0"].ports("o2"))
    channels |= Channel(name="L6-41", port=modules["qcm_bb0"].ports("o3"))
    channels |= Channel(name="L6-42", port=modules["qcm_bb0"].ports("o4"))
    channels |= Channel(name="L6-43", port=modules["qcm_bb1"].ports("o1"))

    channels |= Channel(name="L6-44", port=modules["qcm_bb1"].ports("o2"))
    # channels |= Channel(name="L6-45", port=modules["qcm_bb1"].ports("o3"))
    # channels |= Channel(name="L6-46", port=modules["qcm_bb1"].ports("o4"))
    # #channels |= Channel(name="L6-47", port=modules["qcm_bb0"].ports("o3"))
    # #channels |= Channel(name="L6-48", port=modules["qcm_bb1"].ports("o4"))
    # channels |= Channel(name="L6-47", port=None)
    # channels |= Channel(name="L6-48", port=None)

    # TWPA
    channels |= Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump0

    # channels |= Channel(name="L3-23", port=None)
    # channels["L3-23"].local_oscillator = twpa_pump1

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    for q in range(5):
        qubits[q].readout = channels["L3-20"]
        qubits[q].feedback = channels["L1-1"]
        qubits[q].twpa = channels["L3-10"]
        qubits[q].drive = channels[f"L6-{q+1}"]
        qubits[q].flux = channels[f"L6-{39+q}"]
        channels[f"L6-{39+q}"].qubit = qubits[q]
        qubits[q].flux.max_bias = 2.5
        
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
