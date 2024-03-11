import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A 
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings, load_instrument_settings

ADDRESS = "192.168.0.68"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent


def create():
    """Platform for HTG-ZRF8 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(str(FOLDER), ADDRESS, PORT, sampling_rate=9.8304)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 70

    twpa_pump = SGS100A(name="twpa_pump", address="192.168.0.31")

    instruments = {
        controller.name: controller,
        twpa_pump.name: twpa_pump,
    }
    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-22_ro", port=controller.ports(1))  # readout (DAC)
    channels |= Channel("L1-2-RO", port=controller.ports(0))  # feedback (readout ADC)
    channels |= Channel("L3-22_qd", port=controller.ports(0))  # drive

    # create qubit objects
    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    qubits[0].readout = channels["L3-22_ro"]
    qubits[0].feedback = channels["L1-2-RO"]
    qubits[0].drive = channels["L3-22_qd"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )