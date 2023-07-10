import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.qm import QMOPX
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "qmopx"
ADDRESS = "192.168.0.101:80"
TIME_OF_FLIGHT = 280
RUNCARD = pathlib.Path(__file__).parent / "min25q.yml"


def create(runcard=RUNCARD):
    controller = QMOPX(NAME, ADDRESS, time_of_flight=TIME_OF_FLIGHT)
    # Instantiate local oscillators
    lo3_readout = SGS100A("LO_03", "192.168.0.33")
    lo4_readout = SGS100A("LO_04", "192.168.0.34")
    # twpa_a = SGS100A("LO19", "192.168.0.210", reference_clock_source="external")

    # Create channel objects
    channels = ChannelMap()
    channels |= ("L3-26H", "L3-26L", "L2-1H", "L2-1L")
    # channels["L3-26H"].port = controller[(("con8", 1), ("con8", 2))]
    # channels["L3-26L"].port = controller[(("con7", 1), ("con7", 2))]
    # channels["L2-1H"].port = controller[(("con8", 1), ("con8", 2))]
    # channels["L2-1L"].port = controller[(("con7", 1), ("con7", 2))]
    channels["L3-26H"].port = controller[(("con1", 9), ("con1", 10))]
    channels["L3-26L"].port = controller[(("con2", 9), ("con2", 10))]
    channels["L2-1H"].port = controller[(("con1", 1), ("con1", 2))]
    channels["L2-1L"].port = controller[(("con2", 1), ("con2", 2))]

    # add gain to feedback channels
    channels["L2-1H"].gain = 15
    channels["L2-1L"].gain = 15

    # Configure local oscillator's frequency and power
    lo3_readout.frequency = 7_800_000_000
    lo3_readout.power = 20
    lo4_readout.frequency = 7_100_000_000
    lo4_readout.power = 20

    # Assign local oscillators to channels
    channels["L3-26H"].local_oscillator = lo3_readout
    channels["L2-1H"].local_oscillator = lo3_readout
    channels["L3-26L"].local_oscillator = lo4_readout
    channels["L2-1L"].local_oscillator = lo4_readout

    instruments = [controller, lo3_readout, lo4_readout]
    platform = Platform("min25qA", runcard, instruments, channels)

    # assign channels to qubit
    for q in ["B1", "B2", "B3"]:
        qubit = platform.qubits[q]
        qubit.readout = channels["L3-26L"]
        qubit.feedback = channels["L2-1L"]

    for q in ["B4", "B5"]:
        qubit = platform.qubits[q]
        qubit.readout = channels["L3-26H"]
        qubit.feedback = channels["L2-1H"]

    return platform
