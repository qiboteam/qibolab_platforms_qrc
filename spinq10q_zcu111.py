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

ADDRESS = "192.168.0.81"
PORT = 6000

FOLDER = pathlib.Path(__file__).parent
RUNCARD = pathlib.Path(__file__).parent / "spinq10q-12.yml"


def create(runcard_path=RUNCARD):
    """Platform for ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT)  # , sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 100

    # TURN ON MANUALLY!!!!!!!!!!!!!!!!!!!!!
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    local_oscillator = SGS100A(name="local_oscillator", address="192.168.0.31")
    instruments = {
        controller.name: controller,
        local_oscillator.name: local_oscillator,
        twpa_pump0.name: twpa_pump0,
    }
    # Create channel objects
    channels = ChannelMap()

    # readout
    channels |= Channel("L3-20", port=controller.ports(6))  # probe
    channels |= Channel("L1-1", port=controller.ports(0))  # feedback

    # qubit 1
    channels |= Channel("L6-1", port=controller.ports(4))  # drive
    channels |= Channel("L6-39", port=controller.ports(0))  # flux

    # qubit 2
    channels |= Channel("L6-2", port=controller.ports(3))  # drive
    channels |= Channel("L6-40", port=controller.ports(1))  # flux

    channels["L3-20"].local_oscillator = local_oscillator
    channels["L1-1"].local_oscillator = local_oscillator

    # TWPA
    channels |= Channel(name="twpa", port=None)
    channels["twpa"].local_oscillator = twpa_pump0

    # create qubit objects
    # runcard = load_runcard(FOLDER)
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-20"]
    qubits[1].feedback = channels["L1-1"]
    qubits[1].drive = channels["L6-1"]
    qubits[1].flux = channels["L6-39"]
    qubits[1].twpa = channels["twpa"]

    qubits[2].readout = channels["L3-20"]
    qubits[2].feedback = channels["L1-1"]
    qubits[2].drive = channels["L6-2"]
    qubits[2].flux = channels["L6-40"]
    qubits[2].twpa = channels["twpa"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        "spinq10q_zcu111", qubits, pairs, instruments, settings, resonator_type="2D"
    )
