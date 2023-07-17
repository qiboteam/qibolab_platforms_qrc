import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.qm import QMOPX
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "qmopx"
ADDRESS = "192.168.0.101:80"
TIME_OF_FLIGHT = 280
RUNCARD = pathlib.Path(__file__).parent / "qw25qB.yml"


def create(runcard=RUNCARD):
    """QuantWare 21q chip using Quantum Machines (QM) OPXs and Rohde Schwarz/ERAsynth local oscillators."""
    controller = QMOPX(NAME, ADDRESS, time_of_flight=TIME_OF_FLIGHT)
    lo2 = ERA("ERA_03", "192.168.0.203", reference_clock_source="external")
    lo3 = ERA("ERA_05", "192.168.0.205", reference_clock_source="external")
    lo4 = ERA("ES7", "192.168.0.207", reference_clock_source="external")
    lo_ro_low = SGS100A("LO_04", "192.168.0.34")
    lo_ro_high = SGS100A("LO_09", "192.168.0.39")

    # Create channel objects
    channels = ChannelMap()
    # readout (L=low frequency LO/ H=high frequency LO)
    channels |= Channel("L3-27H", port=controller[(("con1", 10), ("con1", 9))])
    channels |= Channel("L3-27L", port=controller[(("con2", 10), ("con2", 9))])
    # feedback
    channels |= Channel("L2-3H", port=controller[(("con1", 2), ("con1", 1))])
    channels |= Channel("L2-3L", port=controller[(("con2", 2), ("con2", 1))])
    # drive
    channels |= Channel("L3-7", port=controller[(("con1", 2), ("con1", 1))])
    channels |= Channel("L3-8", port=controller[(("con1", 4), ("con1", 3))])
    channels |= Channel("L3-9", port=controller[(("con2", 2), ("con2", 1))])
    channels |= Channel("L3-19", port=controller[(("con1", 6), ("con1", 5))])
    channels |= Channel("L4-22", port=controller[(("con1", 8), ("con1", 7))])
    # flux
    for i in range(1, 6):
        channels |= Channel(f"L1-1{i}", port=controller[(("con3", i),)])

    # add gain to feedback channels
    channels["L2-3L"].gain = 19
    channels["L2-3H"].gain = 19

    # readout
    channels["L3-27H"].local_oscillator = lo_ro_high
    channels["L2-3H"].local_oscillator = lo_ro_high
    channels["L3-27L"].local_oscillator = lo_ro_low
    channels["L2-3L"].local_oscillator = lo_ro_low
    # drive
    channels["L3-7"].local_oscillator = lo3
    channels["L3-8"].local_oscillator = lo3
    channels["L3-9"].local_oscillator = lo4
    channels["L3-19"].local_oscillator = lo2
    channels["L4-22"].local_oscillator = lo2

    lo_ro_low.frequency = int(7.1e9)
    lo_ro_high.frequency = int(7.8e9)
    lo_ro_low.power = 19
    lo_ro_high.power = 19

    instruments = [controller, lo_ro_low, lo_ro_high]
    platform = Platform("qw25qB", runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    # readout low frequency
    for q in ["B1", "B2", "B3"]:
        qubits[q].readout = channels["L3-27L"]
        qubits[q].feedback = channels["L2-3L"]
    # readout high frequency
    for q in ["B4", "B5"]:
        qubits[q].readout = channels["L3-27H"]
        qubits[q].feedback = channels["L2-3H"]
    # drive
    for i in range(1, 4):
        qubits[f"B{i}"].drive = channels[f"L3-{i + 6}"]
    qubits["B4"].drive = channels["L3-19"]
    qubits["B5"].drive = channels["L4-22"]
    # flux
    for i in range(1, 6):
        qubits[f"B{i}"].flux = channels[f"L1-1{i}"]

    return platform
