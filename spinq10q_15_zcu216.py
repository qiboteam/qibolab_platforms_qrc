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

NAME = "zcu216_spinq5q"
ADDRESS = "192.168.0.85"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "spinq10q_15.yml"

TWPA_ADDRESS = "192.168.0.37"
LO_ADDRESS = "192.168.0.35"


def create(runcard_path=RUNCARD):
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-20", port=controller[6])  # readout

    # qubit 1
    channels |= Channel("L1-01-0", port=controller[0])  # feedback
    channels |= Channel("L6-39", port=controller[1])  # flux
    channels |= Channel("L6-1", port=controller[0])  # drive

    # qubit 2
    channels |= Channel("L1-01-1", port=controller[1])  # feedback
    channels |= Channel("L6-40", port=controller[3])  # flux
    channels |= Channel("L6-2", port=controller[4])  # drive

    # qubit 3
    channels |= Channel("L1-01-2", port=controller[2])  # feedback
    channels |= Channel("L6-41", port=controller[5])  # flux
    channels |= Channel("L6-3", port=controller[2])  # drive

    # qubit 4 BAD PORTS
    channels |= Channel("L1-01-3", port=controller[2])  # feedback
    channels |= Channel("L6-42", port=controller[5])  # flux
    channels |= Channel("L6-4", port=controller[2])  # drive

    # qubit 5 BAD PORTS
    channels |= Channel("L1-01-4", port=controller[2])  # feedback
    channels |= Channel("L6-43", port=controller[5])  # flux
    channels |= Channel("L6-5", port=controller[2])  # drive

    twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    readout_lo = SGS100A("readout_lo", LO_ADDRESS)
    channels["L3-20"].local_oscillator = readout_lo

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-20"]
    qubits[1].feedback = channels["L1-01-0"]
    qubits[1].drive = channels["L6-1"]
    qubits[1].flux = channels["L6-39"]

    qubits[2].readout = channels["L3-20"]
    qubits[2].feedback = channels["L1-01-1"]
    qubits[2].drive = channels["L6-2"]
    qubits[2].flux = channels["L6-40"]

    qubits[3].readout = channels["L3-20"]
    qubits[3].feedback = channels["L1-01-2"]
    qubits[3].drive = channels["L6-3"]
    qubits[3].flux = channels["L6-41"]

    qubits[4].readout = channels["L3-20"]
    qubits[4].feedback = channels["L1-01-3"]
    qubits[4].drive = channels["L6-4"]
    qubits[4].flux = channels["L6-42"]

    qubits[5].readout = channels["L3-20"]
    qubits[5].feedback = channels["L1-01-4"]
    qubits[5].drive = channels["L6-5"]
    qubits[5].flux = channels["L6-43"]

    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
        twpa_lo.name: twpa_lo,
    }

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
