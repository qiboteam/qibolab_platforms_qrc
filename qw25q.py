import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.qm import QMOPX
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "qmopx"
ADDRESS = "192.168.0.101:80"
RUNCARD = pathlib.Path(__file__).parent / "qw25q.yml"


def create(runcard=RUNCARD):
    """QuantWare 21q chip using Quantum Machines (QM) OPXs and Rohde Schwarz/ERAsynth local oscillators."""
    # Create channel objects
    channels = ChannelMap()

    # Wiring
    wiring = {
        "feedback": {
            "A": ["L2-1_a", "L2-1_b"],
            "B": ["L2-2_a", "L2-2_b"],
            "C": ["L2-3_a", "L2-3_b"],
            # "D": ["L2-4_a", "L2-4_b"],
        },
        "readout": {
            "A": ["L3-26_a", "L3-26_b"],
            "B": ["L3-27_a", "L3-27_b"],
            "C": ["L3-18_a", "L3-18_b"],
            # "D": ["L3-30_a", "L3-30_b"],
        },
        "drive": {
            "A": [f"L3-{i}" for i in range(1, 7)],
            "B": [f"L3-{i}" for i in range(7, 10)] + ["L3-19", "L4-22"],
            "C": [f"L4-{i}" for i in range(23, 28)],
            # "D": [f"L4-{i}" for i in range(28, 31)],
        },
        "flux": {
            "A": [f"L1-{i}" for i in range(5, 10)] + ["L1-4"],
            "B": [f"L1-{i}" for i in range(11, 16)],
            "C": [f"L1-{i}" for i in range(16, 21)],
            # "D": [f"L1-{i}" for i in range(21, 26)],
        },
    }

    connections = {
        "A": [1, 2, 3],
        "B": [4, 5],
        "C": [6, 7],
        # "D": [8, 9],
    }

    # Create channels
    for channel in wiring:
        for feedline in wiring[channel]:
            for wire in wiring[channel][feedline]:
                channels |= ChannelMap.from_names(wire)

    for feedline in connections:
        channels[wiring["feedback"][feedline][0]].ports = [
            (f"con{connections[feedline][0]}", 2),
            (f"con{connections[feedline][0]}", 1),
        ]
        channels[wiring["feedback"][feedline][1]].ports = [
            (f"con{connections[feedline][1]}", 2),
            (f"con{connections[feedline][1]}", 1),
        ]

        channels[wiring["readout"][feedline][0]].ports = [
            (f"con{connections[feedline][0]}", 10),
            (f"con{connections[feedline][0]}", 9),
        ]
        channels[wiring["readout"][feedline][1]].ports = [
            (f"con{connections[feedline][1]}", 10),
            (f"con{connections[feedline][1]}", 9),
        ]

        # add gain to feedback channels
        channels[wiring["feedback"][feedline][1]].gain = 15
        channels[wiring["feedback"][feedline][0]].gain = 15

        wires_list = wiring["drive"][feedline]
        for i in range(len(wires_list)):
            channels[wires_list[i]].ports = [
                (f"con{connections[feedline][(2*i)//8]}", 2 * i % 8 + 1),
                (f"con{connections[feedline][(2*i)//8]}", 2 * i % 8 + 2),
            ]
            last_port = 2 * i % 8 + 2
            last_con = (2 * i) // 8

        wires_list = wiring["flux"][feedline]
        for i in range(len(wires_list)):
            channels[wires_list[i]].ports = [
                (
                    f"con{connections[feedline][last_con + (i + last_port)//8]}",
                    (i + last_port) % 8 + 1,
                )
            ]

    controller = QMOPX(NAME, ADDRESS)
    # set time of flight for readout integration (HARDCODED)
    controller.time_of_flight = 280

    # Instantiate local oscillators (HARDCODED)
    local_oscillators = [
        ERA(f"era_0{i}", f"192.168.0.20{i}", reference_clock_source="external")
        for i in range(1, 9)
    ]
    local_oscillators.extend(
        SGS100A(f"LO_0{i}", f"192.168.0.3{i}") for i in [1, 3, 4, 5, 6, 9]
    )
    drive_local_oscillators = {
        "A": ["LO_05"] + 2 * ["LO_01"] + ["LO_05"] + ["LO_01"] + ["era_01"],
        "B": ["era_02"] + 4 * ["LO_06"],
        "C": [f"era_0{i}" for i in range(3, 8)],
        # "D": ["era_08"] + 2 * ["LO_01"],
    }
    # Configure local oscillator's frequency and power
    for lo in local_oscillators:
        if lo.name == "LO_01":
            lo.frequency = 6.15e9
            lo.power = 21
        elif lo.name == "LO_04":
            lo.frequency = 7.1e9
            lo.power = 23
        elif lo.name == "LO_03":
            lo.frequency = 7.8e9
            lo.power = 23
        elif lo.name == "LO_05":
            lo.frequency = 5.37e9
            lo.power = 18
        elif lo.name == "LO_06":
            lo.frequency = 6.2e9
            lo.power = 21
        elif "era" in lo.name:
            lo.frequency = 4e9
            lo.power = 15

    # Assign local oscillators to channels
    for lo in local_oscillators:
        if lo.name == "LO_03":
            for feedline in connections:
                channels[wiring["readout"][feedline][0]].local_oscillator = lo
                channels[wiring["feedback"][feedline][0]].local_oscillator = lo
        elif lo.name == "LO_04":
            for feedline in connections:
                channels[wiring["readout"][feedline][1]].local_oscillator = lo
                channels[wiring["feedback"][feedline][1]].local_oscillator = lo
        else:
            for feedline in drive_local_oscillators:
                for i, name in enumerate(drive_local_oscillators[feedline]):
                    if lo.name == name:
                        channels[wiring["drive"][feedline][i]].local_oscillator = lo

    instruments = [controller] + local_oscillators
    platform = Platform("qw25q", runcard, instruments, channels)

    # assign channels to qubits
    qubits = platform.qubits
    for channel in ["flux", "drive"]:
        for feedline in wiring[channel]:
            for i, wire in enumerate(wiring[channel][feedline]):
                q = f"{feedline}{i+1}"
                if channel == "flux":
                    qubits[q].flux = channels[wire]
                    channels[wire].qubit = qubits[q]
                elif channel == "drive":
                    qubits[q].drive = channels[wire]
                    if "era" in qubits[q].drive.local_oscillator.name:
                        qubits[q].drive.local_oscillator.frequency = (
                            qubits[q].drive_frequency + 200e6
                        )

    for q in [
        "A3",
        "A5",
        "A6",
        "B4",
        "B5",
        "C2",
        "C3",
        "C5",
    ]:  # Qubits with LO around 7e9
        qubits[q].readout = channels[wiring["readout"][q[0]][0]]
        qubits[q].feedback = channels[wiring["feedback"][q[0]][0]]
    for q in [
        "A1",
        "A2",
        "A4",
        "B1",
        "B2",
        "B3",
        "C1",
        "C4",
    ]:  # Qubits with LO around 7.5e9
        qubits[q].readout = channels[wiring["readout"][q[0]][1]]
        qubits[q].feedback = channels[wiring["feedback"][q[0]][1]]

    return platform
