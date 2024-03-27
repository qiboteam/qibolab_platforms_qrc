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

NAME = "spinq10q_15_zcu216"
ADDRESS = "192.168.0.93"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent 

TWPA_ADDRESS = "192.168.0.37"
#LO_ADDRESS = "192.168.0.35"


def create():
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    runcard = load_runcard(FOLDER)
    # Instantiate QICK instruments
    controller = RFSoC("ZCU216", ADDRESS, PORT)
    controller.cfg.ro_time_of_flight = 200
    controller.cfg.relaxation_time = 200
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

    channels |= Channel("L3-20-1", port=controller.ports(10))  # readout probe
    channels |= Channel("L3-20-2", port=controller.ports(11))  # readout probe
    channels |= Channel("L3-20-3", port=controller.ports(12))  # readout probe
    channels |= Channel("L3-20-4", port=controller.ports(13))  # readout probe
    channels |= Channel("L3-20-5", port=controller.ports(14))  # readout probe
    # qubit 1
    channels |= Channel("L1-1-1", port=controller.ports(4))  # feedback
    channels |= Channel("L6-39", port=controller.ports(0))  # flux
    channels |= Channel("L6-1", port=controller.ports(8))  # drive

    # qubit 2
    channels |= Channel("L1-1-2", port=controller.ports(5))  # feedback
    channels |= Channel("L6-40", port=controller.ports(1))  # flux
    channels |= Channel("L6-2", port=controller.ports(9))  # drive

    # qubit 3
    channels |= Channel("L1-1-3", port=controller.ports(6))  # feedback
    channels |= Channel("L6-41", port=controller.ports(2))  # flux
    channels |= Channel("L6-3", port=controller.ports(14))  # drive

    # qubit 4
    channels |= Channel("L1-1-4", port=controller.ports(7))  # feedback
    channels |= Channel("L6-42", port=controller.ports(3))  # flux
    channels |= Channel("L6-4", port=controller.ports(15))  # drive

    # qubit 5
    channels |= Channel("L1-1-5", port=controller.ports(0))  # feedback
    channels |= Channel("L6-43", port=controller.ports(4))  # flux
    channels |= Channel("L6-5", port=controller.ports(5))  # drive    
    # TWPA
    channels |= Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump
    #readout_lo = SGS100A("readout_lo", LO_ADDRESS)
    #channels["L3-21"].local_oscillator = readout_lo

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-20-1"]
    qubits[1].feedback = channels["L1-1-1"]
    qubits[1].twpa = channels["L3-10"]
    qubits[1].drive = channels["L6-1"]
    qubits[1].flux = channels["L6-39"]

    qubits[2].readout = channels["L3-20-2"]
    qubits[2].feedback = channels["L1-1-2"]
    qubits[2].twpa = channels["L3-10"]    
    qubits[2].drive = channels["L6-2"]
    qubits[2].flux = channels["L6-40"]

    qubits[3].readout = channels["L3-20-3"]
    qubits[3].feedback = channels["L1-1-3"]
    qubits[3].twpa = channels["L3-10"]   
    qubits[3].drive = channels["L6-3"]
    qubits[3].flux = channels["L6-41"]

    qubits[4].readout = channels["L3-20-4"]
    qubits[4].feedback = channels["L1-1-4"]
    qubits[4].twpa = channels["L3-10"]    
    qubits[4].drive = channels["L6-4"]
    qubits[4].flux = channels["L6-42"]

    qubits[5].readout = channels["L3-20-5"]
    qubits[5].feedback = channels["L1-1-5"]
    qubits[5].twpa = channels["L3-10"]
    qubits[5].drive = channels["L6-5"]
    qubits[5].flux = channels["L6-43"]



    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(str(FOLDER), qubits, pairs, instruments, settings, resonator_type="2D")