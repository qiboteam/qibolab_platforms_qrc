import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A as LocalOscillator
from qibolab.platform import Platform

NAME = "tii_rfsoc4x2"
ADDRESS = "192.168.0.72"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii1q_b1.yml"

TWPA_ADDRESS = "192.168.0.32"


def create(runcard=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-18_ro", port=controller[0])  # readout (DAC)
    channels |= Channel("L2-RO", port=controller[0])  # feedback (readout DAC)
    channels |= Channel("L3-18_qd", port=controller[1])  # drive

    local_oscillators = [
        LocalOscillator("twpa_a", TWPA_ADDRESS),
    ]
    local_oscillators[0].frequency = 6_200_000_000
    local_oscillators[0].power = -1

    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    instruments = [controller] + local_oscillators
    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-18_ro"]
    qubits[0].feedback = channels["L2-RO"]
    qubits[0].drive = channels["L3-18_qd"]

    return platform
