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

ADDRESS = "192.168.1.77"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent
NAME = str(FOLDER)
RUNCARD = FOLDER


def create(runcard_path=RUNCARD):
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC("ZCU216", ADDRESS, PORT)
    # controller.cfg.ro_time_of_flight = 0  # tProc clock ticks?!!
    controller.cfg.ro_time_of_flight = 275 + 138  # tProc clock ticks?!! 789ns (lag included)
    # controller.cfg.relaxation_time = 100  # in us !!

    instruments = {
        controller.name: controller,
    }

    # DRIVE       = [0, 1, 2]
    # PROBE_CH    = 3
    # FEEDBACK_CH = [0, 1, 2]


    # Create channel objects
    channels = ChannelMap()

    # readout
    # base_TII3q_v3.bit
    channels |= Channel("L3-20", port=controller.ports("RFO_3"))  # probe 0_230
    channels |= Channel("L1-1-1", port=controller.ports("RFI_0"))  # feedback 1_230
    channels |= Channel("L1-1-2", port=controller.ports("RFI_1"))  # feedback 2_230
    channels |= Channel("L1-1-3", port=controller.ports("RFI_2"))  # feedback 3_230
    # # base_MTS_14.bit
    # channels |= Channel("L3-20", port=controller.ports("RFO_6"))  # probe 0_230 OK
    # channels |= Channel("L1-1-1", port=controller.ports("RFI_0"))  # feedback 0_228
    # channels |= Channel("L1-1-2", port=controller.ports("RFI_1"))  # feedback 1_228
    # channels |= Channel("L1-1-3", port=controller.ports("RFI_2"))  # feedback 3_229

    # drive
    channels |= Channel("L6-1", port=controller.ports("RFO_0"))  # q1
    channels |= Channel("L6-2", port=controller.ports("RFO_1"))  # q2
    channels |= Channel("L6-3", port=controller.ports("RFO_2"))  # q3

    # create qubit objects
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["q1"].readout = channels["L3-20"]
    qubits["q1"].feedback = channels["L1-1-1"]
    qubits["q1"].drive = channels["L6-1"]
    qubits["q2"].readout = channels["L3-20"]
    qubits["q2"].feedback = channels["L1-1-2"]
    qubits["q2"].drive = channels["L6-2"]
    qubits["q3"].readout = channels["L3-20"]
    qubits["q3"].feedback = channels["L1-1-3"]
    qubits["q3"].drive = channels["L6-3"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
