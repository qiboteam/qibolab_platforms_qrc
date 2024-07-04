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

NAME = "spinq10q_12__zcu111"
ADDRESS = "192.168.1.81"
PORT = 6000
LO_ADDRESS = "192.168.0.34"
TWPA_ADDRESS = "192.168.0.37"
FOLDER = pathlib.Path(__file__).parent


def create():
    """Platform for qubits 1,2,3 on spinq10q chip using the  ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """

    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT, sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 100


    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-20_ro", port=controller.ports(6))  # probe  dac6
    # QUBIT 1
    channels |= Channel("L1-1-RO_0", port=controller.ports(0))  # feedback adc0
    channels |= Channel("L6-1_qd", port=controller.ports(3))  # drive    dac3
    channels |= Channel("L6-39_fl", port=controller.ports(0))  # flux     dac0
    # QUBIT 2
    channels |= Channel("L1-1-RO_1", port=controller.ports(1))  # feedback adc1
    channels |= Channel("L6-2_qd", port=controller.ports(4))  # drive    dac4
    channels |= Channel("L6-40_fl", port=controller.ports(1))  # flux     dac1
    # QUBIT 3
    channels |= Channel("L1-1-RO_2", port=controller.ports(2))  # feedback adc2
    channels |= Channel("L6-3_qd", port=controller.ports(5))  # drive    dac5
    channels |= Channel("L6-41_fl", port=controller.ports(2))  # flux     dac2

    # Readout local oscillator
    local_oscillator = SGS100A(name="LO", address=LO_ADDRESS)
    channels["L3-20_ro"].local_oscillator = local_oscillator
    #TWPA
    twpa_pump0 = SGS100A(name="twpa_pump0", address=TWPA_ADDRESS)
    #channels["L3-10"].twpa_pump0 = twpa_pump0 
    # create qubit objects
    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    qubits[1].readout = channels["L3-20_ro"]
    qubits[1].feedback = channels["L1-1-RO_0"]
    qubits[1].drive = channels["L6-1_qd"]
    qubits[1].flux = channels["L6-39_fl"]
    #qubits[1].twpa = channels["L3-10"]
    channels["L6-39_fl"].qubit = qubits[1]

    qubits[2].readout = channels["L3-20_ro"]
    qubits[2].feedback = channels["L1-1-RO_1"]
    qubits[2].drive = channels["L6-2_qd"]
    qubits[2].flux = channels["L6-40_fl"]
    #qubits[2].twpa = channels["L3-10"]
    channels["L6-40_fl"].qubit = qubits[2]

    qubits[3].readout = channels["L3-20_ro"]
    qubits[3].feedback = channels["L1-1-RO_2"]
    qubits[3].drive = channels["L6-3_qd"]
    qubits[3].flux = channels["L6-41_fl"]
    #qubits[3].twpa = channels["L3-10"]
    channels["L6-41_fl"].qubit = qubits[3]

    instruments = {controller.name: controller, 
                    twpa_pump0.name: twpa_pump0,
                    local_oscillator.name: local_oscillator}
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
