import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "tii_zcu111"
ADDRESS = "192.168.0.81"
PORT = 6000
LO_ADDRESS = "192.168.0.212"

FOLDER = pathlib.Path(__file__).parent


def create(folder: pathlib.Path = FOLDER):
    """Platform for ZCU111 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """

    # Instantiate QICK instruments
    controller = RFSoC(str(folder), ADDRESS, PORT, sampling_rate=6.144)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 100

    # Create channel objects
    channels = ChannelMap()
    channels |= Channel("L3-30_ro", port=controller.ports(6))  # readout  dac6
    # QUBIT 0
    channels |= Channel("L2-4-RO_0", port=controller.ports(0))  # feedback adc0
    channels |= Channel("L4-29_qd", port=controller.ports(3))  # drive    dac3
    channels |= Channel("L1-22_fl", port=controller.ports(0))  # flux     dac0
    # QUBIT 1
    channels |= Channel("L2-4-RO_1", port=controller.ports(1))  # feedback adc1
    channels |= Channel("L4-30_qd", port=controller.ports(4))  # drive    dac4
    channels |= Channel("L1-23_fl", port=controller.ports(1))  # flux     dac1
    # QUBIT 2
    channels |= Channel("L2-4-RO_2", port=controller.ports(2))  # feedback adc2
    channels |= Channel("L4-31_qd", port=controller.ports(5))  # drive    dac5
    channels |= Channel("L1-24_fl", port=controller.ports(2))  # flux     dac2

    # Readout local oscillator
    local_oscillator = ERA("ErasynthLO", LO_ADDRESS, ethernet=True)
    channels["L3-30_ro"].local_oscillator = local_oscillator

    # create qubit objects
    runcard = load_runcard(folder)
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    qubits[0].readout = channels["L3-30_ro"]
    qubits[0].feedback = channels["L2-4-RO_0"]
    qubits[0].drive = channels["L4-29_qd"]
    qubits[0].flux = channels["L1-22_fl"]
    channels["L1-22_fl"].qubit = qubits[0]

    qubits[1].readout = channels["L3-30_ro"]
    qubits[1].feedback = channels["L2-4-RO_1"]
    qubits[1].drive = channels["L4-30_qd"]
    qubits[1].flux = channels["L1-23_fl"]
    channels["L1-23_fl"].qubit = qubits[1]

    qubits[2].readout = channels["L3-30_ro"]
    qubits[2].feedback = channels["L2-4-RO_2"]
    qubits[2].drive = channels["L4-31_qd"]
    qubits[2].flux = channels["L1-24_fl"]
    channels["L1-24_fl"].qubit = qubits[2]

    instruments = {controller.name: controller, local_oscillator.name: local_oscillator}
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(folder), qubits, pairs, instruments, settings, resonator_type="2D"
    )
