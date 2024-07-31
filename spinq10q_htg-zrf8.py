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

ADDRESS = "192.168.1.68"
PORT = 6000

FOLDER = pathlib.Path(__file__).parent
RUNCARD = pathlib.Path(__file__).parent / "spinq10q-12.yml"


def create(runcard_path=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT)  # , sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 350
    controller.cfg.repetition_duration = 200

    # TURN ON MANUALLY!!!!!!!!!!!!!!!!!!!!!
    # twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    instruments = {
        controller.name: controller,
        # twpa_pump0.name: twpa_pump0,
    }
    # Create channel objects
    channels = ChannelMap()

    # readout
    channels |= Channel("L3-20", port=controller.ports(0))  # probe
    channels |= Channel("L1-1", port=controller.ports(1))  # feedback

    # qubit 1
    channels |= Channel("L6-1", port=controller.ports(2))  # drive
    channels |= Channel("L6-39", port=controller.ports(3))  # flux

    # qubit 2
    channels |= Channel("L6-2", port=controller.ports(1))  # drive
    channels |= Channel("L6-40", port=controller.ports(5))  # flux

    # create qubit objects
    # runcard = load_runcard(FOLDER)
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-20"]
    qubits[1].feedback = channels["L1-1"]
    qubits[1].drive = channels["L6-1"]
    qubits[1].flux = channels["L6-39"]
    # qubits[1].twpa = channels[""]

    qubits[2].readout = channels["L3-20"]
    qubits[2].feedback = channels["L1-1"]
    qubits[2].drive = channels["L6-2"]
    qubits[2].flux = channels["L6-40"]
    # qubits[2].twpa = channels[""]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        "spinq10q_htg-zrf8", qubits, pairs, instruments, settings, resonator_type="3D"
    )
