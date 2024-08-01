import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

ADDRESS = "192.168.1.77"
TWPA_ADDRESS = "192.168.0.37"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent
# # alvaro/latest_20231215
# NAME = "spinq10q_14_zcu216"
# RUNCARD = pathlib.Path(__file__).parent / "spinq10q-15.yml"
# # main
NAME = str(FOLDER)
RUNCARD = FOLDER


def create(runcard_path=RUNCARD):
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC("ZCU216", ADDRESS, PORT)
    controller.cfg.ro_time_of_flight = 167  # tProc clock ticks?!!
    controller.cfg.relaxation_time = 100  # in us !!

    twpa_pump0 = SGS100A(name="twpa_pump0", address=TWPA_ADDRESS)
    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }

    # Create channel objects
    channels = ChannelMap()

    # readout
    channels |= Channel("L3-20", port=controller.ports(6))  # probe
    channels |= Channel("L1-1-1", port=controller.ports(0))  # feedback
    channels |= Channel("L1-1-2", port=controller.ports(1))  # feedback
    channels |= Channel("L1-1-3", port=controller.ports(2))  # feedback
    channels |= Channel("L1-1-4", port=controller.ports(3))  # feedback

    # # qubit 1
    channels |= Channel("L6-1", port=controller.ports(3))  # drive
    channels |= Channel("L6-39", port=controller.ports(1))  # flux

    # qubit 2
    channels |= Channel("L6-2", port=controller.ports(4))  # drive
    channels |= Channel("L6-40", port=controller.ports(3))  # flux

    # qubit 3
    channels |= Channel("L6-3", port=controller.ports(5))  # drive
    channels |= Channel("L6-41", port=controller.ports(0))  # flux

    # qubit 4
    channels |= Channel("L6-4", port=controller.ports(2))  # flux
    channels |= Channel("L6-42", port=controller.ports(2))  # drive

    # TWPA
    channels |= Channel(name="twpa", port=None)
    channels["twpa"].local_oscillator = twpa_pump0

    # create qubit objects
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-20"]
    qubits[1].feedback = channels["L1-1-1"]
    qubits[1].drive = channels["L6-1"]
    qubits[1].flux = channels["L6-39"]
    qubits[1].twpa = channels["twpa"]

    qubits[2].readout = channels["L3-20"]
    qubits[2].feedback = channels["L1-1-2"]
    qubits[2].drive = channels["L6-2"]
    qubits[2].flux = channels["L6-40"]
    qubits[2].twpa = channels["twpa"]

    qubits[3].readout = channels["L3-20"]
    qubits[3].feedback = channels["L1-1-3"]
    qubits[3].drive = channels["L6-3"]
    qubits[3].flux = channels["L6-41"]
    qubits[3].twpa = channels["twpa"]

    qubits[4].readout = channels["L3-20"]
    qubits[4].feedback = channels["L1-1-4"]
    qubits[4].drive = channels["L6-4"]
    qubits[4].flux = channels["L6-42"]
    qubits[4].twpa = channels["twpa"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
