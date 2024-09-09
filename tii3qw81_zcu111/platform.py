import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.instruments.rfsoc import RFSoC
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)
#from qibolab.kernels import Kernels

NAME = "tii3qw81__zcu111"
ADDRESS = "192.168.0.81"
PORT = 6000
LO_ADDRESS = "192.168.0.31"
#TWPA_ADDRESS = "192.168.0.37"
FOLDER = pathlib.Path(__file__).parent


def create():
    """Platform for qubits 2 and 3 on tii3qw81 chip using the  ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """

    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT, sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 100


    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-28_ro", port=controller.ports(6))  # probe  dac6

    # QUBIT 2
    channels |= Channel("L1-2-RO_1", port=controller.ports(1))  # feedback adc1
    channels |= Channel("L4-31_qd", port=controller.ports(3))  # drive    dac3

    # QUBIT 3
    channels |= Channel("L1-2-RO_2", port=controller.ports(2))  # feedback adc2
    channels |= Channel("L4-32_qd", port=controller.ports(4))  # drive    dac4


    # Readout local oscillator
    local_oscillator = SGS100A(name="LO", address=LO_ADDRESS)
    channels["L3-20_ro"].local_oscillator = local_oscillator




    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)
 

    qubits[2].readout = channels["L3-20_ro"]
    qubits[2].feedback = channels["L1-1-RO_1"]
    qubits[2].drive = channels["L6-2_qd"]


    qubits[3].readout = channels["L3-20_ro"]
    qubits[3].feedback = channels["L1-1-RO_2"]
    qubits[3].drive = channels["L6-3_qd"]




    instruments = {controller.name: controller, 
                    local_oscillator.name: local_oscillator}
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
