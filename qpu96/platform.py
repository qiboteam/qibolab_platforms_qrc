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
NUM_QUBITS = 3

ROOT = pathlib.Path.home()

def create():
    """"QRC QFoundry 2Q Chip for Cross Resonance Gates"""
    runcard = load_runcard(FOLDER)

    # Declare RF Instrument
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:6"),  # feedline
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:17"),  # q0, q1 
        "qcm_rf1": QcmRf("qrm_rf1", f"{ADDRESS}:4"),  # q2   
    }
    controller = QbloxController("qblox_controller", 
                                 ADDRESS, 
                                 modules)
    
    # Declare TWPA Inatrument
    # twpa = SGS100A(name="twpa", address="192.168.0.36")
 
    #  Define the instruments and update all modules with the platform settings
    instruments = {
        controller.name: controller,
        # twpa.name: twpa
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
    channels |= Channel(name="drive2", port=modules["qcm_rf1"].ports("o1")) # qubit
    channels |= Channel(name="dummy", port=modules["qcm_rf1"].ports("o2")) # qubit
    #channels |= Channel(name="dummy", port=modules["qrm_rf1"].ports("o2",out=False))

    # Channel for TWPA Pump
    # channels |= Channel(name="twpa", port=None)
    # channels["twpa"].local_oscillator = twpa

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
 
    # assign channels to qubits    
    for q, qubit in qubits.items():
        qubit.readout = channels["feed_in"]
        qubit.feedback = channels["feed_back"]
        qubit.drive = channels[f"drive{q}"]
        # qubit.twpa = channels["twpa"]
        channels[f"drive{q}"].qubit = qubit
    
    settings = load_settings(runcard)
    #instruments["qblox_controller"].device

    # DEBUG: ###################################################################
    # import os
    # from datetime import datetime

    # debug_folder = f"{ROOT}/debug/{PLATFORM}/"
    # if not os.path.exists(debug_folder):
    #     os.makedirs(debug_folder)
    # for name in modules:
    #     modules[name]._debug_folder = debug_folder
    #########################################################################################################
    return Platform(
        PLATFORM, qubits, pairs, instruments, settings, resonator_type="D"
    )