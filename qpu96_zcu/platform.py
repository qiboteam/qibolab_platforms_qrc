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

ADDRESS = "192.168.0.77"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent
NAME = str(FOLDER)
RUNCARD = FOLDER

nqubits = 3
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
    channels |= Channel("readout",     port=controller.ports("RFO_0"))  # probe 0_230
    channels |= Channel("feedback0",   port=controller.ports("RFI_0"))  # feedback 1_230
    channels |= Channel("feedback1",   port=controller.ports("RFI_1"))  # feedback 2_230
    channels |= Channel("feedback2",   port=controller.ports("RFI_2"))  # feedback 3_230

    # drive
    for qubit in range(nqubits):
        channels |= Channel(f"drive{qubit}", port=controller.ports(f"RFO_{qubit+1}"))  # drive# = RFO_{#+1}

    # create qubit objects
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    for qubit in range(nqubits):
        qubits[qubit].readout  = channels[f"readout"]
        qubits[qubit].feedback = channels[f"feedback{qubit}"]
        qubits[qubit].drive    = channels[f"drive{qubit}"]
        # channels[f"drive{qubit}"].qubit = qubits[qubit]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
