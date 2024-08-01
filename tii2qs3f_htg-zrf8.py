import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
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
RUNCARD = pathlib.Path(__file__).parent / "tii2qs3f.yml"


def create(runcard_path=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT)  # , sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 350
    controller.cfg.repetition_duration = 200

    instruments = {
        controller.name: controller,
    }
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-27", port=controller.ports(1))  # readout

    # qubit 1
    channels |= Channel("L2-03-1", port=controller.ports(1))  # feedback
    # channels |= Channel("L1-6", port=controller.ports(3))  # flux
    channels |= Channel("L3-5", port=controller.ports(2))  # drive

    # qubit 2
    channels |= Channel("L2-03-2", port=controller.ports(1))  # feedback
    channels |= Channel("L1-22", port=controller.ports(3))  # flux
    channels |= Channel("L3-6", port=controller.ports(5))  # drive

    # create qubit objects
    # runcard = load_runcard(FOLDER)
    runcard = load_runcard(RUNCARD)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[1].readout = channels["L3-27"]
    qubits[1].feedback = channels["L2-03-1"]
    qubits[1].drive = channels["L3-5"]
    # qubits[1].flux = channels["L1-6"]

    qubits[2].readout = channels["L3-27"]
    qubits[2].feedback = channels["L2-03-2"]
    qubits[2].drive = channels["L3-6"]
    qubits[2].flux = channels["L1-22"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        "tii2qs3f_htg-zrf8", qubits, pairs, instruments, settings, resonator_type="3D"
    )
