import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.platform import Platform

NAME = "tii_zcu111"
ADDRESS = "192.168.0.81"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu111.yml"

LO_ADDRESS = "192.168.0.212"


def create(runcard=RUNCARD):
    """Platform for ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Create channel objects
    channels = ChannelMap()

    # Readout channel
    channels |= ChannelMap.from_names("L3-30_ro")  # dac6

    # QUBIT 0
    channels |= "L2-4-RO_0"  # feedback adc0
    channels |= "L4-29_qd"  # drive    dac3
    channels |= "L1-22_fl"  # flux     dac0
    # QUBIT 1
    channels |= "L2-4-RO_1"  # feedback adc1
    channels |= "L4-30_qd"  # drive    dac4
    channels |= "L1-23_fl"  # flux     dac1
    # QUBIT 2
    channels |= "L2-4-RO_2"  # feedback adc2
    channels |= "L4-31_qd"  # drive    dac5
    channels |= "L1-24_fl"  # flux     dac2

    # Map controllers to qubit channels (HARDCODED)
    channels["L3-30_ro"].ports = [("dac6", 6)]

    # Qubit 0
    channels["L2-4-RO_0"].ports = [("adc0", 0)]
    channels["L4-29_qd"].ports = [("dac3", 3)]
    channels["L1-22_fl"].ports = [("dac0", 0)]
    # Qubit 1
    channels["L2-4-RO_1"].ports = [("adc1", 1)]
    channels["L4-30_qd"].ports = [("dac4", 4)]
    channels["L1-23_fl"].ports = [("dac1", 1)]
    # Qubit 2
    channels["L2-4-RO_2"].ports = [("adc2", 2)]
    channels["L4-31_qd"].ports = [("dac5", 5)]
    channels["L1-24_fl"].ports = [("dac2", 2)]

    local_oscillators = [
        ERA("ErasynthLO", LO_ADDRESS, ethernet=True),
    ]

    # Instantiate QICK instruments
    controller = RFSoC("tii_zcu111", ADDRESS, PORT)

    # Readout local oscillator
    local_oscillators[0].frequency = 7_500_000_000
    local_oscillators[0].power = 10
    channels["L3-30_ro"].local_oscillator = local_oscillators[0]

    instruments = [controller] + local_oscillators

    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-30_ro"]
    qubits[0].feedback = channels["L2-4-RO_0"]
    qubits[0].drive = channels["L4-29_qd"]
    qubits[0].flux = channels["L1-22_fl"]
    channels["L1-22_fl"].qubit = qubits[0]

    qubits[1].readout = channels["L3-30_ro"]
    qubits[1].feedback = channels["L2-4-RO_1"]
    qubits[1].drive = channels["L4-30_qd"]
    qubits[1].flux = channels["L1-23_fl"]
    channels["L1-23_fl"].qubit = qubits[1]

    qubits[2].readout = channels["L3-30_ro"]
    qubits[2].feedback = channels["L2-4-RO_2"]
    qubits[2].drive = channels["L4-31_qd"]
    qubits[2].flux = channels["L1-24_fl"]
    channels["L1-24_fl"].qubit = qubits[2]

    return platform
