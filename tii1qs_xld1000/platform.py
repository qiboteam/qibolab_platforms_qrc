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

NAME = "tii1qs_xld1000_rfsoc4x2"
ADDRESS = "192.168.0.72"
PORT = 6000
FOLDER = pathlib.Path(__file__).parent


def create():
    """Platform for RFSoC4x2 board running qibosoq with the chip TII1QS_XLD1000

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)

    controller = RFSoC(str(FOLDER), ADDRESS, PORT, sampling_rate=9.8304)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 70
    # twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    instruments = {
        controller.name: controller,
        #     twpa_pump0.name: twpa_pump0,
    }

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-31r", port=controller.ports(1))  # readout (DAC)
    # Feedback
    channels |= Channel(name="L2-1", port=controller.ports(0))  # feedback (readout ADC)
    # Drive
    channels |= Channel(name="L3-31d", port=controller.ports(0))  # drive

    #channels |= Channel(name="L99", port=modules["qcm_rf0"].ports("i1", out=False))

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )