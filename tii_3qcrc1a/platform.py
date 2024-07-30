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
 
PLATFORM = "tii_3qcrc1a"
ADDRESS = "192.168.0.2"
FOLDER  = pathlib.Path(__file__).parent
 
 
def create():
    """"QRC QFoundry 2Q Chip for Cross Resonance Gates"""
    runcard = load_runcard(FOLDER)

    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:1"),  # feedline
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:10"),  # q1, q2,  for now
        "qrm_rf1": QrmRf("qrm_rf1", f"{ADDRESS}:2"),  # q3
        "qrm_rf2": QrmRf("qrm_rf2", f"{ADDRESS}:3"),  # qw
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
    channels |= Channel(name="V1", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="W3", port=modules["qrm_rf0"].ports("i1",out=False))
     # Drive
    channels |= Channel(name="W1", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="W2", port=modules["qcm_rf0"].ports("o2"))

    channels |= Channel(name="W4", port=modules["qrm_rf1"].ports("o1"))
    channels |= Channel(name="V4", port=modules["qrm_rf2"].ports("o1"))
 
    channels |= Channel(name="dummy1", port=modules["qrm_rf1"].ports("i1",out=False))
    channels |= Channel(name="dummy2", port=modules["qrm_rf2"].ports("i1",out=False))
    
    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
 
    # assign channels to qubits    
    for q in range(0, 4):  # q0, q1
        qubits[q].readout = channels["V1"]
        qubits[q].feedback = channels["W3"]
    
    qubits[0].drive = channels[f"W1"]
    qubits[1].drive = channels[f"W2"]
    qubits[2].drive = channels[f"W4"]
    qubits[3].drive = channels[f"V4"]

    channels[f"W1"].qubit = qubits[0]
    channels[f"W2"].qubit = qubits[1]
    channels[f"W4"].qubit = qubits[2]
    channels[f"V4"].qubit = qubits[3]
 
    settings = load_settings(runcard)
 
    #instruments["qblox_controller"].device

    return Platform(
        PLATFORM, qubits, pairs, instruments, settings, resonator_type="2D"
    )