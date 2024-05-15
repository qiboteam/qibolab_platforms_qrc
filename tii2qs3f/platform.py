
import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import HDAWG, PQSC, SHFQC
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

N_QUBITS = 2


def create():
    """Tii 2q chip"""

    device_setup = DeviceSetup("ZURO_BLANCO")
    # Dataserver
    device_setup.add_dataserver(host="localhost", port=8004)
    # Instruments
    device_setup.add_instruments(
        HDAWG("device_hdawg", address="DEV8660"),
        PQSC("device_pqsc", address="DEV10055", reference_clock_source="internal"),
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
    device_setup.add_connections(
        "device_hdawg",
        create_connection(to_signal="q1/flux_line", ports=f"SIGOUTS/0"),
    )


    device_setup.add_connections(
        "device_pqsc",
        create_connection(to_instrument="device_hdawg", ports="ZSYNCS/0"),
        create_connection(to_instrument="device_shfqc", ports="ZSYNCS/2"),
    )

    controller = Zurich(
        "EL_ZURO",
        device_setup=device_setup,
        time_of_flight=75,
        smearing=50,
    )

    # Create channel objects and map controllers
    channels = ChannelMap()
    # feedback
    channels |= Channel(
        "L2-2", port=controller.ports(("device_shfqc", "[QACHANNELS/0/INPUT]"))
    )
    # readout
    channels |= Channel(
        "L3-26", port=controller.ports(("device_shfqc", "[QACHANNELS/0/OUTPUT]"))
    )
    # drive
    channels |= (
        Channel(
            f"L3-{3+i}",
            port=controller.ports(("device_shfqc", f"SGCHANNELS/{i}/OUTPUT")),
        )
        for i in range(N_QUBITS)
    )
    # flux qubits
    channels |= Channel("L1-5", port=controller.ports(("device_hdawg", "SIGOUTS/0")))

    # readout "gain"
    channels["L3-26"].power_range = 10
    # feedback "gain"
    channels["L2-2"].power_range = 5

    # drive
    channels["L3-3"].power_range = -20
    channels["L3-4"].power_range = 5

    # flux
    channels["L1-5"].power_range = 1

    # Instantiate local oscillators
    local_oscillators = [
        DummyLocalOscillator("lo_readout", None), 
        DummyLocalOscillator("lo_drive", None)
        ]


    # Map LOs to channels
    ch_to_lo = {
        "L3-26": 0,
        "L3-3": 1,
        "L3-4": 1,
    }
    for ch, lo in ch_to_lo.items():
        channels[ch].local_oscillator = local_oscillators[lo]

    # create qubit objects
    runcard = load_runcard(FOLDER)
    qubits, _, pairs = load_qubits(runcard)
    settings = load_settings(runcard)

    # assign channels to qubits
    for i in range(N_QUBITS):
        qubits[i].readout = channels["L3-26"]
        qubits[i].feedback = channels["L2-2"]
        qubits[i].drive = channels[f"L3-{3 + i}"]
    qubits[1].flux = channels["L1-5"]
    channels["L1-5"].qubit = qubits[1]


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
    )
