import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "tii_zcu216"
ADDRESS = "192.168.0.85"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216.yml"

LO_ADDRESS = "192.168.0.35"


def create(runcard=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 190
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-18", port=controller[7])  # readout

    # qubit C4
    channels |= Channel("L2-04-0", port=controller[0])  # feedback
    channels |= Channel("L1-19", port=controller[1])  # flux
    channels |= Channel("L4-26", port=controller[5])  # drive

    readout_lo = SGS100A("LO", LO_ADDRESS)
    readout_lo.frequency = 7.5e9
    readout_lo.power = 10
    channels["L3-18"].local_oscillator = readout_lo

    local_oscillators = [readout_lo]
    instruments = [controller] + local_oscillators

    platform = Platform(NAME, runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    qubits[0].readout = channels["L3-18"]
    qubits[0].feedback = channels["L2-04-0"]
    qubits[0].drive = channels["L4-26"]
    qubits[0].flux = channels["L1-19"]

    return platform
