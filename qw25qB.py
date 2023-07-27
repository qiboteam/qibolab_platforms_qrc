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
    lo2 = SGS100A("LO_2", "192.168.0.32")
    lo3 = SGS100A("LO_3", "192.168.0.33")
    es7 = ERA("ES7", "192.168.0.207", reference_clock_source="external")
    lo4 = SGS100A("LO_04", "192.168.0.34")
    lo9 = SGS100A("LO_09", "192.168.0.39")
    twpa = SGS100A("LO_06", "192.168.0.36")

    # Create channel objects
    channels = ChannelMap()
    # readout (L=low frequency LO/ H=high frequency LO)
    channels |= Channel("L3-27H", port=controller[(("con1", 10), ("con1", 9))])
    channels |= Channel("L3-27L", port=controller[(("con2", 10), ("con2", 9))])
    # feedback
    channels |= Channel("L2-3H", port=controller[(("con1", 2), ("con1", 1))])
    channels |= Channel("L2-3L", port=controller[(("con2", 2), ("con2", 1))])
    # drive
    channels |= Channel("L3-7", port=controller[(("con1", 1), ("con1", 2))])
    channels |= Channel("L3-8", port=controller[(("con1", 3), ("con1", 4))])
    channels |= Channel("L3-9", port=controller[(("con2", 1), ("con2", 2))])
    channels |= Channel("L3-19", port=controller[(("con1", 5), ("con1", 6))])
    channels |= Channel("L4-22", port=controller[(("con1", 7), ("con1", 8))])
    # flux
    for i in range(1, 6):
        channels |= Channel(f"L1-1{i}", port=controller[(("con3", i),)])

    # add gain to feedback channels
    channels["L2-3H"].gain = 0
    channels["L2-3L"].gain = 0

    # readout
    lo4.frequency = int(7.1e9)
    lo9.frequency = int(7.8e9)
    lo4.power = 20
    lo9.power = 20
    channels["L3-27H"].local_oscillator = lo9
    channels["L2-3H"].local_oscillator = lo9
    channels["L3-27L"].local_oscillator = lo4
    channels["L2-3L"].local_oscillator = lo4
    # drive
    channels["L3-7"].local_oscillator = lo3  # B1
    channels["L3-8"].local_oscillator = lo2  # B2
    channels["L3-9"].local_oscillator = lo3  # B3
    channels["L3-19"].local_oscillator = es7  # B4
    channels["L4-22"].local_oscillator = lo2  # B5

    # for B1/B3
    lo3.power = 20
    lo3.frequency = int(5.2e9)

    # for B4
    es7.power = 20
    es7.frequency = int(7.0e9)

    # for B2/B5
    lo2.power = 20
    lo2.frequency = int(6.3e9)

    # twpa
    twpa.frequency = int(6.482e9)
    twpa.power = 2

    instruments = [controller, lo4, lo9, twpa, lo2, lo3, es7]
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
