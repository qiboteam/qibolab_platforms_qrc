import itertools
import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import SHFQC
from laboneq.simple import DeviceSetup
from qibolab import Platform
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.dummy import DummyLocalOscillator
from qibolab.instruments.zhinst import Zurich
from qibolab.kernels import Kernels
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent

N_QUBITS = 1


def create():
    """1q non flux tunable chip controlled Zurich Instruments (Zh) SHFQC.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    device_setup = DeviceSetup("EL_ZURO")
    # Dataserver
    device_setup.add_dataserver(host="localhost", port=8004)
    # Instruments
    device_setup.add_instruments(
        SHFQC("device_shfqc", address="DEV12146"),
    )
    device_setup.add_connections(
        "device_shfqc",
        *[
            create_connection(
                to_signal=f"q{i}/drive_line", ports=[f"SGCHANNELS/{i}/OUTPUT"]
            )
            for i in range(N_QUBITS)
        ],
        *[
            create_connection(
                to_signal=f"q{i}/measure_line", ports=["QACHANNELS/0/OUTPUT"]
            )
            for i in range(N_QUBITS)
        ],
        *[
            create_connection(
                to_signal=f"q{i}/acquire_line", ports=["QACHANNELS/0/INPUT"]
            )
            for i in range(N_QUBITS)
        ],
    )

    controller = Zurich(
        "EL_ZURO",
        device_setup=device_setup,
        use_emulation=False,
        time_of_flight=200,  # TODO: Calibrate this
        smearing=0,  # TODO: Calibrate this
    )

    # Create channel objects and map controllers
    channels = ChannelMap()
    # feedback
    channels |= Channel(
        "L2-1", port=controller.ports(("device_shfqc", "[QACHANNELS/0/INPUT]"))
    )
    # readout
    channels |= Channel(
        "L3-31r", port=controller.ports(("device_shfqc", "[QACHANNELS/0/OUTPUT]"))
    )
    # drive
    channels |= Channel(
        f"L3-31d", port=controller.ports(("device_shfqc", f"SGCHANNELS/{0}/OUTPUT"))
    )

    # SHFQC
    # Sets the maximal Range of the Signal Output power.

    # readout "gain": play with the power range to calibrate the best RO
    channels["L3-31r"].power_range = -30  # -15
    # feedback "gain": set to max power range (10 Dbm) if no distorsion
    channels["L2-1"].power_range = 10

    # drive
    channels["L3-31d"].power_range = -5  # q0

    # Instantiate local oscillators
    local_oscillators = [
        DummyLocalOscillator(f"lo_{kind}", None)
        for kind in ["readout"] + [f"drive_{n}" for n in range(1)]
    ]

    # Map LOs to channels
    ch_to_lo = {
        "L3-31r": 0,
        "L3-31d": 1,
    }
    for ch, lo in ch_to_lo.items():
        channels[ch].local_oscillator = local_oscillators[lo]

    # create qubit objects
    runcard = load_runcard(FOLDER)
    kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard, kernels)
    settings = load_settings(runcard)

    # assign channels to qubits
    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    instruments = {controller.name: controller}
    instruments.update({lo.name: lo for lo in local_oscillators})
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="2D",
        couplers=couplers,
    )
