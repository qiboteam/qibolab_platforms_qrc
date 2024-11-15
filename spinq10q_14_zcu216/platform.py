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

ADDRESS = "192.168.1.78"
TWPA_ADDRESS = "192.168.0.37"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent

# # alvaro/latest_20231215
# NAME = "spinq10q_14_zcu216"
# RUNCARD = pathlib.Path(__file__).parent / "spinq10q-15.yml"

# # main
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

    twpa_pump0 = SGS100A(name="twpa_pump0", address=TWPA_ADDRESS)
    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }

# DC_FLUX     = [5,    2,    6, 7] new
# RF_FLUX     = [None, 0, None, 1]
# DRIVE       = [3,    4,    5, 2]
# PROBE_CH    = 6
# FEEDBACK_CH = [0,    1,    2, 3] #ADC


    # Create channel objects
    channels = ChannelMap()

    # readout
    channels |= Channel("L3-20", port=controller.ports("RFO_6"))  # probe
    channels |= Channel("L1-1-1", port=controller.ports("RFI_0"))  # feedback
    channels |= Channel("L1-1-2", port=controller.ports("RFI_1"))  # feedback
    channels |= Channel("L1-1-3", port=controller.ports("RFI_2"))  # feedback
    channels |= Channel("L1-1-4", port=controller.ports("RFI_3"))  # feedback

    # drive
    channels |= Channel("L6-1", port=controller.ports("RFO_3"))  # q1
    channels |= Channel("L6-2", port=controller.ports("RFO_4"))  # q2
    channels |= Channel("L6-3", port=controller.ports("RFO_5"))  # q3
    channels |= Channel("L6-4", port=controller.ports("RFO_2"))  # q4
    
    # flux
    channels |= Channel("L6-39", port=controller.ports("DCO_5"))        # q1
    channels |= Channel("L6-40", port=controller.ports("DCO_2:RFO_0"))  # q2
    channels |= Channel("L6-41", port=controller.ports("DCO_6"))        # q3
    channels |= Channel("L6-42", port=controller.ports("DCO_7:RFO_1"))  # q4

    # TWPA
    channels |= Channel(name="twpa", port=None)
    channels["twpa"].local_oscillator = twpa_pump0

    # create qubit objects
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["q1"].readout = channels["L3-20"]
    qubits["q1"].feedback = channels["L1-1-1"]
    qubits["q1"].drive = channels["L6-1"]
    qubits["q1"].flux = channels["L6-39"]
    qubits["q1"].twpa = channels["twpa"]
    qubits["q2"].readout = channels["L3-20"]
    qubits["q2"].feedback = channels["L1-1-2"]
    qubits["q2"].drive = channels["L6-2"]
    qubits["q2"].flux = channels["L6-40"]
    qubits["q2"].twpa = channels["twpa"]
    qubits["q3"].readout = channels["L3-20"]
    qubits["q3"].feedback = channels["L1-1-3"]
    qubits["q3"].drive = channels["L6-3"]
    qubits["q3"].flux = channels["L6-41"]
    qubits["q3"].twpa = channels["twpa"]
    qubits["q4"].readout = channels["L3-20"]
    qubits["q4"].feedback = channels["L1-1-4"]
    qubits["q4"].drive = channels["L6-4"]
    qubits["q4"].flux = channels["L6-42"]
    qubits["q4"].twpa = channels["twpa"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
