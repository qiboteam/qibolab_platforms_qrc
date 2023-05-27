import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.platform import Platform
from qibolab.instruments.rfsoc import TII_RFSOC4x2
from qibolab.instruments.rohde_schwarz import SGS100A as LocalOscillator

NAME = "tii_rfsoc4x2"
ADDRESS = "192.168.0.72:6000"
RUNCARD = pathlib.Path(__file__).parent / "tii1q_b1.yml"


def create(runcard=RUNCARD):
    """Platform using QICK project on the RFSoC4x2 board.
    
    IPs and other instrument related parameters are hardcoded in.
    """
    # Create channel objects
    channels = ChannelMap()
    channels |= "L3-18_ro"  # readout (DAC)
    channels |= "L2-RO"     # feedback (readout DAC)
    channels |= "L3-18_qd"  # drive

    # Map controllers to qubit channels (HARDCODED)
    channels["L3-18_ro"].ports = [("o0", 0)]  # readout
    channels["L2-RO"].ports = [("i0", 0)]  # feedback
    channels["L3-18_qd"].ports = [("o1", 1)]  # drive

    local_oscillators = [
        LocalOscillator("twpa_a", "192.168.0.32"),
    ]
    local_oscillators[0].frequency = 6_200_000_000
    local_oscillators[0].power = -1

    # Instantiate QICK instruments
    controller = TII_RFSOC4x2(NAME, ADDRESS)
    instruments = [controller] + local_oscillators
    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-18_ro"]
    qubits[0].feedback = channels["L2-RO"]
    qubits[0].drive = channels["L3-18_qd"]

    return platform