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
FOLDER  = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name


def create():
    """"QRC QFoundry 2Q Chip for Cross Resonance Gates"""
    runcard = load_runcard(FOLDER)

    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:4"),  # feedline
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:20"),  # q2, q3
        "qrm_rf1": QrmRf("qrm_rf1", f"{ADDRESS}:6"),  # q1
        "qrm_rf2": QrmRf("qrm_rf2", f"{ADDRESS}:6"),  # qw
    }


    controller = QbloxController("qblox_controller", ADDRESS, modules)
    #twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
 
    controller.modules["qrm_rf0"].device



    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)
 
    # #########################################################################################################
 
    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="V2", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="W5", port=modules["qrm_rf0"].ports("i1",out=False))

     # Drive
    channels |= Channel(name="V5", port=modules["qrm_rf1"].ports("o1")) #q1
    channels |= Channel(name="V6", port=modules["qcm_rf0"].ports("o1")) #q2
    channels |= Channel(name="V7", port=modules["qcm_rf0"].ports("o2")) #q3
    channels |= Channel(name="dummy", port=modules["qrm_rf2"].ports("o1")) #qw (not connected)

    channels |= Channel(name="dummy2", port=modules["qrm_rf1"].ports("i1",out=False))
    channels |= Channel(name="dummy3", port=modules["qrm_rf2"].ports("i1",out=False))
    
    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
 
    # assign channels to qubits    
    for q in range(0, 4):  # q0, q1
        qubits[q].readout = channels["V2"]
        qubits[q].feedback = channels["W5"]
    
    qubits[0].drive = channels[f"V5"]
    qubits[1].drive = channels[f"V6"]
    qubits[2].drive = channels[f"V7"]
    qubits[3].drive = channels[f"dummy"]

    channels[f"V5"].qubit = qubits[0]
    channels[f"V6"].qubit = qubits[1]
    channels[f"V7"].qubit = qubits[2]
    channels[f"dummy"].qubit = qubits[3]
 
    settings = load_settings(runcard)
 
    #instruments["qblox_controller"].device

    return Platform(
        PLATFORM, qubits, pairs, instruments, settings, resonator_type="2D"
    )