import itertools
import pathlib

from qibolab import Platform
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.oscillator import LocalOscillator
from qibolab.instruments.zhinst import Zurich
from qibolab.serialize import load_qubits, load_runcard, load_settings

RUNCARD = pathlib.Path(__file__).parent / "iqm5q.yml"

TWPA_ADDRESS = "192.168.0.210"


def create(runcard_path=RUNCARD):
    """IQM 5q-chip controlled Zurich Instrumetns (Zh) SHFQC, HDAWGs and PQSC.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    # Instantiate Zh set of instruments[They work as one]
    instruments = {
        "SHFQC": [{"address": "DEV12146", "uid": "device_shfqc"}],
        "HDAWG": [
            {"address": "DEV8660", "uid": "device_hdawg"},
            {"address": "DEV8673", "uid": "device_hdawg2"},
        ],
        "PQSC": [{"address": "DEV10055", "uid": "device_pqsc"}],
    }

    shfqc = []
    for i in range(5):
        shfqc.append(
            {"iq_signal": f"q{i}/drive_line", "ports": f"SGCHANNELS/{i}/OUTPUT"}
        )
        shfqc.append(
            {"iq_signal": f"q{i}/measure_line", "ports": ["QACHANNELS/0/OUTPUT"]}
        )
        shfqc.append(
            {"acquire_signal": f"q{i}/acquire_line", "ports": ["QACHANNELS/0/INPUT"]}
        )

    hdawg = []
    for i in range(5):
        hdawg.append({"rf_signal": f"q{i}/flux_line", "ports": f"SIGOUTS/{i}"})
    for c, i in zip(itertools.chain(range(0, 2), range(3, 4)), range(5, 8)):
        hdawg.append({"rf_signal": f"qc{c}/flux_line", "ports": f"SIGOUTS/{i}"})

    hdawg2 = [{"rf_signal": "qc4/flux_line", "ports": f"SIGOUTS/0"}]

    pqsc = [
        "internal_clock_signal",
        {"to": "device_hdawg2", "port": "ZSYNCS/4"},
        {"to": "device_hdawg", "port": "ZSYNCS/2"},
        {"to": "device_shfqc", "port": "ZSYNCS/0"},
    ]

    connections = {
        "device_shfqc": shfqc,
        "device_hdawg": hdawg,
        "device_hdawg2": hdawg2,
        "device_pqsc": pqsc,
    }

    descriptor = {
        "instruments": instruments,
        "connections": connections,
    }

    controller = Zurich(
        "EL_ZURO",
        descriptor,
        use_emulation=False,
        time_of_flight=75,
        smearing=50,  # time_of_flight=280, smearing=100
    )

    # Create channel objects and map controllers
    channels = ChannelMap()
    # readout
    channels |= Channel(
        "L3-31", port=controller[("device_shfqc", "[QACHANNELS/0/INPUT]")]
    )
    # feedback
    channels |= Channel(
        "L2-7", port=controller[("device_shfqc", "[QACHANNELS/0/OUTPUT]")]
    )
    # drive
    channels |= (
        Channel(
            f"L4-{i}", port=controller[("device_shfqc", f"SGCHANNELS/{i-5}/OUTPUT")]
        )
        for i in range(15, 20)
    )
    # flux qubits (CAREFUL WITH THIS !!!)
    channels |= (
        Channel(f"L4-{i}", port=controller[("device_hdawg", f"SIGOUTS/{i-6}")])
        for i in range(6, 11)
    )
    # flux couplers
    channels |= (
        Channel(f"L4-{i}", port=controller[("device_hdawg", f"SIGOUTS/{i-11+5}")])
        for i in range(11, 14)
    )
    channels |= Channel("L4-14", port=controller[("device_hdawg2", f"SIGOUTS/0")])

    # TWPA pump(EraSynth)
    channels |= Channel("L3-32")

    # SHFQC
    # Sets the maximal Range of the Signal Output power.
    # The instrument selects the closest available Range with a resolution of 5 dBm.

    # feedback
    channels["L3-31"].power_range = 10
    # readout
    channels["L2-7"].power_range = -25
    # drive
    for i in range(5, 10):
        channels[f"L4-1{i}"].power_range = -10
    channels[f"L4-19"].power_range = 0

    # HDAWGS
    # Sets the output voltage range.
    # The instrument selects the next higher available Range with a resolution of 0.4 Volts.

    # flux
    for i in range(6, 11):
        channels[f"L4-{i}"].power_range = 0.8
    # flux couplers
    for i in range(11, 15):
        channels[f"L4-{i}"].power_range = 0.8

    # Instantiate local oscillators
    local_oscillators = [
        LocalOscillator(f"lo_{kind}", None)
        for kind in ["readout"] + [f"drive_{n}" for n in range(4)]
    ]

    local_oscillators.append(ERA("twpa_fixed", TWPA_ADDRESS))
    # TWPA Parameters
    local_oscillators[-1].frequency = 6_690_000_000
    local_oscillators[-1].power = -5.6

    # Set Dummy LO parameters (Map only the two by two oscillators)
    local_oscillators[0].frequency = 5_500_000_000  # For SG0 (Readout)
    local_oscillators[1].frequency = 4_200_000_000  # For SG1 and SG2 (Drive)
    local_oscillators[2].frequency = 4_600_000_000  # For SG3 and SG4 (Drive)
    local_oscillators[3].frequency = 4_800_000_000  # For SG5 and SG6 (Drive)

    # Map LOs to channels
    ch_to_lo = {
        "L2-7": 0,
        "L4-15": 1,
        "L4-16": 1,
        "L4-17": 2,
        "L4-18": 2,
        "L4-19": 3,
        "L3-32": 4,
    }
    for ch, lo in ch_to_lo.items():
        channels[ch].local_oscillator = local_oscillators[lo]

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)
    # assign channels to qubits and sweetspots(operating points)
    qubits = platform.qubits
    for q in range(0, 5):
        qubits[q].feedback = channels["L3-31"]
        qubits[q].readout = channels["L2-7"]

    for q in range(0, 5):
        qubits[q].drive = channels[f"L4-{15 + q}"]
        qubits[q].flux = channels[f"L4-{6 + q}"]
        channels[f"L4-{6 + q}"].qubit = qubits[q]

    # assign channels to couplers and sweetspots(operating points)
    for c in range(0, 2):
        qubits[f"c{c}"].flux = channels[f"L4-{11 + c}"]
        channels[f"L4-{11 + c}"].qubit = qubits[f"c{c}"]
    for c in range(3, 5):
        qubits[f"c{c}"].flux = channels[f"L4-{10 + c}"]
        channels[f"L4-{10 + c}"].qubit = qubits[f"c{c}"]

    # assign qubits to couplers
    for c in itertools.chain(range(0, 2), range(3, 5)):
        qubits[f"c{c}"].flux_coupler = [qubits[c]]
        qubits[f"c{c}"].flux_coupler.append(qubits[2])

    instruments = {controller.name: controller}
    instruments.update({lo.name: lo for lo in local_oscillators})
    settings = load_settings(runcard)
    return Platform("IQM5q", qubits, pairs, instruments, settings, resonator_type="2D")
