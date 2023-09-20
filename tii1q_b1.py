import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A as LocalOscillator
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings

NAME = "tii_rfsoc4x2"
ADDRESS = "192.168.0.72"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii1q_b1.yml"


def create(runcard_path=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 70
    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-22_ro", port=controller[1])  # readout (DAC)
    channels |= Channel("L1-2-RO", port=controller[0])  # feedback (readout ADC)
    channels |= Channel("L3-22_qd", port=controller[0])  # drive

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)
    # assign channels to qubits
    qubits[0].readout = channels["L3-22_ro"]
    qubits[0].feedback = channels["L1-2-RO"]
    qubits[0].drive = channels["L3-22_qd"]

    instruments = {controller.name: controller}
    settings = load_settings(runcard)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")
