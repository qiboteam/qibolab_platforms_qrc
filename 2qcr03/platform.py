import pathlib

from qibolab.channels import Channel, ChannelMap

from qibolab.platform import Platform

from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController

from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "2QRC03"
ADDRESS = "192.168.0.2"
FOLDER = pathlib.Path(__file__).parent


def create():
    """TII 2Qubit Chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:1"), 
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:10"),
          }
    
    # Instantiate instruments
    controller = QbloxController("qblox_controller", ADDRESS, modules)

    instruments = {
        controller.name: controller,
   #     twpa_pump0.name: twpa_pump0,
    }
    instruments.update(modules)

    # Create channel objects
    channels = ChannelMap()

    # Readout
    channels |= Channel(name="w7", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="v1", port=modules["qrm_rf0"].ports("i1"))
    # Drive
    channels |= Channel(name="w4", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="w5", port=modules["qcm_rf0"].ports("o2"))
   
    # create qubit objects
    qubits,couplers, pairs = load_qubits(runcard)


    # assign channels to qubits
    qubits[0].readout = channels["w7"]
    qubits[0].feedback = channels["v1"]
    qubits[0].drive = channels["w4"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
