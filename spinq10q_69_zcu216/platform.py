import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

ADDRESS = "192.168.1.85"
TWPA_ADDRESS = "192.168.0.39"
PORT = 6000
# NAME = "spinq10q_69_zcu216"
FOLDER = pathlib.Path(__file__).parent
NAME = str(FOLDER)
RUNCARD = FOLDER


def create():
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC("ZCU216", ADDRESS, PORT)
    # controller.cfg.ro_time_of_flight = 0  # tProc clock ticks?!!
    controller.cfg.ro_time_of_flight = 275 + 138  # tProc clock ticks?!! 789ns (lag included)
    # controller.cfg.relaxation_time = 100  # in us !!

    twpa_pump1 = SGS100A(name="twpa_pump1", address=TWPA_ADDRESS)
    instruments = {
        controller.name: controller,
        twpa_pump1.name: twpa_pump1,
    }

    # Create channel objects
    channels = ChannelMap()

    # readout
    channels |= Channel("L3-21", port=controller.ports("RFO_6"))  # probe
    channels |= Channel("L2-17-6", port=controller.ports("RFI_0"))  # feedback
    channels |= Channel("L2-17-7", port=controller.ports("RFI_1"))  # feedback
    channels |= Channel("L2-17-8", port=controller.ports("RFI_2"))  # feedback
    channels |= Channel("L2-17-9", port=controller.ports("RFI_3"))  # feedback

    # drive
    channels |= Channel("L6-6", port=controller.ports("RFO_3"))  # q6
    channels |= Channel("L6-7", port=controller.ports("RFO_4"))  # q7
    channels |= Channel("L6-8", port=controller.ports("RFO_5"))  # q8
    channels |= Channel("L6-9", port=controller.ports("RFO_2"))  # q9
    
    # flux
    channels |= Channel("L6-44", port=controller.ports("DCO_2:RFO_0"))  # q6
    channels |= Channel("L6-45", port=controller.ports("DCO_5"))        # q7
    channels |= Channel("L6-46", port=controller.ports("DCO_6:RFO_1"))  # q8
    channels |= Channel("L6-47", port=controller.ports("DCO_7"))        # q9

    # TWPA
    channels |= Channel(name="L3-23", port=None)
    channels["L3-23"].local_oscillator = twpa_pump1

    # create qubit objects
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["q6"].readout = channels["L3-21"]
    qubits["q6"].feedback = channels["L2-17-6"]
    qubits["q6"].twpa = channels["L3-23"]
    qubits["q6"].drive = channels["L6-6"]
    qubits["q6"].flux = channels["L6-44"]
    qubits["q7"].readout = channels["L3-21"]
    qubits["q7"].feedback = channels["L2-17-7"]
    qubits["q7"].twpa = channels["L3-23"]
    qubits["q7"].drive = channels["L6-7"]
    qubits["q7"].flux = channels["L6-45"]
    qubits["q8"].readout = channels["L3-21"]
    qubits["q8"].feedback = channels["L2-17-8"]
    qubits["q8"].twpa = channels["L3-23"]
    qubits["q8"].drive = channels["L6-8"]
    qubits["q8"].flux = channels["L6-46"]
    qubits["q9"].readout = channels["L3-21"]
    qubits["q9"].feedback = channels["L2-17-9"]
    qubits["q9"].twpa = channels["L3-23"]
    qubits["q9"].drive = channels["L6-9"]
    qubits["q9"].flux = channels["L6-47"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
