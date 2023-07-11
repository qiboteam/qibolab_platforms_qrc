import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA as LocalOscillator
from qibolab.instruments.rfsoc import RFSoC
from qibolab.platform import Platform

NAME = "tii_zcu216"
ADDRESS = "192.168.2.85"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216.yml"

# LO_ADDRESS = "192.168.0.212"


def create(runcard=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 150
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-18_ro", port=controller[6])  # readout (DAC)
    channels |= Channel("L2-RO", port=controller[0])  # feedback (readout ADC)
    channels |= Channel("L3-18_qd", port=controller[4])  # drive

    local_oscillators = []

    instruments = [controller] + local_oscillators
    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-18_ro"]
    qubits[0].feedback = channels["L2-RO"]
    qubits[0].drive = channels["L3-18_qd"]

    return platform
