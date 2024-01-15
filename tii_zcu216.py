import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "tii_zcu216"
ADDRESS = "192.168.0.85"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216.yml"

TWPA_ADDRESS = "192.168.0.31"
LO_ADDRESS = "192.168.0.35"


def create(runcard_path=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT, sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-30", port=controller.ports(6))  # readout

    # qubit D1
    channels |= Channel("L2-01-0", port=controller.ports(0))  # feedback
    channels |= Channel("L1-21", port=controller.ports(1))  # flux
    channels |= Channel("L4-28", port=controller.ports(0))  # drive

    # qubit D2
    channels |= Channel("L2-01-1", port=controller.ports(1))  # feedback
    channels |= Channel("L1-22", port=controller.ports(3))  # flux
    channels |= Channel("L4-29", port=controller.ports(4))  # drive

    # qubit D3
    channels |= Channel("L2-01-2", port=controller.ports(2))  # feedback
    channels |= Channel("L1-23", port=controller.ports(5))  # flux
    channels |= Channel("L4-30", port=controller.ports(2))  # drive

    twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    readout_lo = SGS100A("readout_lo", LO_ADDRESS)
    channels["L3-30"].local_oscillator = readout_lo

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["D1"].readout = channels["L3-30"]
    qubits["D1"].feedback = channels["L2-01-0"]
    qubits["D1"].drive = channels["L4-28"]
    qubits["D1"].flux = channels["L1-21"]

    qubits["D2"].readout = channels["L3-30"]
    qubits["D2"].feedback = channels["L2-01-1"]
    qubits["D2"].drive = channels["L4-29"]
    qubits["D2"].flux = channels["L1-22"]

    qubits["D3"].readout = channels["L3-30"]
    qubits["D3"].feedback = channels["L2-01-2"]
    qubits["D3"].drive = channels["L4-30"]
    qubits["D3"].flux = channels["L1-23"]

    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
        twpa_lo.name: twpa_lo,
    }

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
