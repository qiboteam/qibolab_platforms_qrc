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

NAME = "spinq10q_610_zcu216"
ADDRESS = "192.168.0.93"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent

TWPA_ADDRESS = "192.168.0.39"


def create():
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    runcard = load_runcard(FOLDER)
    # Instantiate QICK instruments
    controller = RFSoC("ZCU216", ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    #
    twpa_pump = SGS100A(name="twpa_pump", address=TWPA_ADDRESS)
    #
    instruments = {
        controller.name: controller,
        #    readout_lo.name: readout_lo,
        twpa_pump.name: twpa_pump,
    }

    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-21-6", port=controller.ports(10))  # readout probe
    channels |= Channel("L3-21-7", port=controller.ports(11))  # readout probe
    channels |= Channel("L3-21-8", port=controller.ports(12))  # readout probe
    channels |= Channel("L3-21-9", port=controller.ports(13))  # readout probe
    channels |= Channel("L3-21-10", port=controller.ports(14))  # readout probe
    # qubit 6
    channels |= Channel("L2-17-6", port=controller.ports(4))  # feedback
    channels |= Channel("L6-44", port=controller.ports(1))  # flux
    channels |= Channel("L6-6", port=controller.ports(9))  # drive

    # qubit 7
    channels |= Channel("L2-17-7", port=controller.ports(5))  # feedback
    channels |= Channel("L6-45", port=controller.ports(3))  # flux
    channels |= Channel("L6-7", port=controller.ports(10))  # drive

    # qubit 8
    channels |= Channel("L2-17-8", port=controller.ports(6))  # feedback
    channels |= Channel("L6-46", port=controller.ports(5))  # flux
    channels |= Channel("L6-8", port=controller.ports(11))  # drive

    # qubit 9
    channels |= Channel("L2-17-9", port=controller.ports(7))  # feedback
    channels |= Channel("L6-47", port=controller.ports(0))  # flux
    channels |= Channel("L6-9", port=controller.ports(12))  # drive

    # qubit 10
    channels |= Channel("L2-17-10", port=controller.ports(0))  # feedback
    channels |= Channel("L6-48", port=controller.ports(0))  # flux
    channels |= Channel("L6-10", port=controller.ports(13))  # drive
    # TWPA
    channels |= Channel(name="L3-23", port=None)
    channels["L3-23"].local_oscillator = twpa_pump
    # readout_lo = SGS100A("readout_lo", LO_ADDRESS)
    # channels["L3-21"].local_oscillator = readout_lo

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[6].readout = channels["L3-21-6"]
    qubits[6].feedback = channels["L2-17-6"]
    qubits[6].twpa = channels["L3-23"]
    qubits[6].drive = channels["L6-6"]
    qubits[6].flux = channels["L6-44"]

    qubits[7].readout = channels["L3-21-7"]
    qubits[7].feedback = channels["L2-17-7"]
    qubits[7].twpa = channels["L3-23"]
    qubits[7].drive = channels["L6-7"]
    qubits[7].flux = channels["L6-45"]

    qubits[8].readout = channels["L3-21-8"]
    qubits[8].feedback = channels["L2-17-8"]
    qubits[8].twpa = channels["L3-23"]
    qubits[8].drive = channels["L6-8"]
    qubits[8].flux = channels["L6-46"]

    qubits[9].readout = channels["L3-21-9"]
    qubits[9].feedback = channels["L2-17-9"]
    qubits[9].twpa = channels["L3-23"]
    qubits[9].drive = channels["L6-9"]
    qubits[9].flux = channels["L6-47"]

    qubits[10].readout = channels["L3-21-10"]
    qubits[10].feedback = channels["L2-17-10"]
    qubits[10].twpa = channels["L3-23"]
    qubits[10].drive = channels["L6-10"]
    qubits[10].flux = channels["L6-48"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D"
    )
