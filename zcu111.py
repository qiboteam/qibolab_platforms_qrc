import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "zcu111"
ADDRESS = "192.168.0.81"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "zcu111.yml"

# ERA local oscillator at 192.168.0.212
LO_ADDRESS = "192.168.0.212"
TWPA_ADDRESS = "192.168.0.31"


def create(runcard=RUNCARD):
    """Platform for ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """

    # Instantiate QICK instruments
    controller = RFSoC("tii_zcu111", ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 150
    controller.cfg.repetition_duration = 70

    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-30_ro", port=controller[6])  # readout  dac6
    # QUBIT 0
    channels |= Channel("L2-1-RO_0", port=controller[0])  # feedback adc0
    channels |= Channel("L4-29_qd", port=controller[3])  # drive    dac3
    channels |= Channel("L1-22_fl", port=controller[0])  # flux     dac0
    # QUBIT 1
    channels |= Channel("L2-1-RO_1", port=controller[1])  # feedback adc1
    channels |= Channel("L4-30_qd", port=controller[4])  # drive    dac4
    channels |= Channel("L1-23_fl", port=controller[1])  # flux     dac1
    # QUBIT 2
    channels |= Channel("L2-1-RO_2", port=controller[2])  # feedback adc2
    channels |= Channel("L4-31_qd", port=controller[5])  # drive    dac5
    channels |= Channel("L1-24_fl", port=controller[2])  # flux     dac2

    local_oscillators = [
        ERA("ErasynthLO", LO_ADDRESS),
        SGS100A("TWPA", TWPA_ADDRESS),
    ]

    # Readout local oscillator
    local_oscillators[0].frequency = 7_500_000_000
    local_oscillators[0].power = 10
    channels["L3-30_ro"].local_oscillator = local_oscillators[0]

    local_oscillators[1].frequency = 5_300_000_000
    local_oscillators[1].power = -5

    instruments = [controller] + local_oscillators

    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-30_ro"]
    qubits[0].feedback = channels["L2-1-RO_0"]
    qubits[0].drive = channels["L4-29_qd"]
    qubits[0].flux = channels["L1-22_fl"]
    channels["L1-22_fl"].qubit = qubits[0]

    qubits[1].readout = channels["L3-30_ro"]
    qubits[1].feedback = channels["L2-1-RO_1"]
    qubits[1].drive = channels["L4-30_qd"]
    qubits[1].flux = channels["L1-23_fl"]
    channels["L1-23_fl"].qubit = qubits[1]

    qubits[2].readout = channels["L3-30_ro"]
    qubits[2].feedback = channels["L2-1-RO_2"]
    qubits[2].drive = channels["L4-31_qd"]
    qubits[2].flux = channels["L1-24_fl"]
    channels["L1-24_fl"].qubit = qubits[2]

    return platform
