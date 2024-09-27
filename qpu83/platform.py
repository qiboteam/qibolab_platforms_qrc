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
 
ADDRESS = "192.168.0.2"
FOLDER  = pathlib.Path(__file__).parent
PLATFORM = FOLDER.name
NUM_QUBITS = 2

def create():
    """"QRC QFoundry 2Q Chip for Cross Resonance Gates"""
    runcard = load_runcard(FOLDER)

    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:2"),  # feedline
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:10"),  # x, q2    
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    #twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
 
    device = controller.modules["qrm_rf0"].device

    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)
 
    # #########################################################################################################
 
    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="feed_in", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="feed_back", port=modules["qrm_rf0"].ports("i1",out=False))

     # Drive
    channels |= Channel(name="drive0", port=modules["qcm_rf0"].ports("o1")) # 
    channels |= Channel(name="drive1", port=modules["qcm_rf0"].ports("o2")) # qubit
    
    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
 
    # assign channels to qubits    
    for q in range(0, NUM_QUBITS):
        qubits[q].readout = channels["feed_in"]
        qubits[q].feedback = channels["feed_back"]
        qubits[q].drive = channels[f"drive{q}"]
        channels[f"drive{q}"].qubit = qubits[q]

    settings = load_settings(runcard)
 
    #instruments["qblox_controller"].device

    return Platform(
        PLATFORM, qubits, pairs, instruments, settings, resonator_type="2D"
    )