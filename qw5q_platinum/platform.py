import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import HDAWG, PQSC, SHFQC
from laboneq.simple import DeviceSetup
from qibolab import Platform
from qibolab.channels import Channel
from qibolab.instruments.dummy import DummyLocalOscillator
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.instruments.zhinst import Zurich
from qibolab.kernels import Kernels
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent


def create():
    """"""

    device_setup = DeviceSetup("EL_ZURO")
    device_setup.add_dataserver(host="localhost", port=8004)
    device_setup.add_instruments(
        HDAWG("device_hdawg", address="DEV8660"),
        PQSC("device_pqsc", address="DEV10055", reference_clock_source="internal"),
        SHFQC("device_shfqc", address="DEV12146"),
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

    # create qubit objects
    runcard = load_runcard(FOLDER)
    kernels = Kernels.load(FOLDER)
    qubits, _, pairs = load_qubits(runcard, kernels)
    settings = load_settings(runcard)

    twpa_pump_channel = Channel("twpa_pump")
    measure_path = "QACHANNELS/0/OUTPUT"
    acquire_path = "QACHANNELS/0/INPUT"
    measure_channel = Channel(
        f"measure", controller.ports(("device_shfqc", measure_path))
    )
    acquire_channel = Channel(
        f"acquire", controller.ports(("device_shfqc", acquire_path))
    )
    for i in range(5):
        drive_path = f"SGCHANNELS/{i}/OUTPUT"
        device_setup.add_connections(
            "device_shfqc",
            create_connection(to_signal=f"q{i}/drive_line", ports=[drive_path]),
            create_connection(to_signal=f"q{i}/measure_line", ports=[measure_path]),
            create_connection(to_signal=f"q{i}/acquire_line", ports=[acquire_path]),
        )

        flux_path = f"SIGOUTS/{i}"
        device_setup.add_connections(
            "device_hdawg",
            create_connection(to_signal=f"q{i}/flux_line", ports=[flux_path]),
        )

        qubits[i].drive = Channel(
            f"q{i}/drive", controller.ports(("device_shfqc", drive_path))
        )
        qubits[i].readout = measure_channel
        qubits[i].feedback = acquire_channel
        qubits[i].flux = Channel(
            f"q{i}/flux", controller.ports(("device_hdawg", flux_path))
        )

        qubits[i].twpa = twpa_pump_channel

    qubits[0].drive.local_oscillator = DummyLocalOscillator("q_0_1/drive/lo", None)
    qubits[1].drive.local_oscillator = qubits[0].drive.local_oscillator
    qubits[2].drive.local_oscillator = DummyLocalOscillator("q_2_3/drive/lo", None)
    qubits[3].drive.local_oscillator = qubits[2].drive.local_oscillator
    qubits[4].drive.local_oscillator = DummyLocalOscillator("q_4/drive/lo", None)

    arbitrary_qubit = next(iter(qubits.values()))
    arbitrary_qubit.readout.local_oscillator = DummyLocalOscillator("readout/lo", None)
    arbitrary_qubit.twpa.local_oscillator = SGS100A("twpa", "192.168.0.38")

    measure_channel.power_range = -10
    acquire_channel.power_range = 0
    for qb in qubits.values():
        qb.drive.power_range = 10 #-10 #-5 #0
        qb.flux.power_range = 4
         #5

    instruments = {controller.name: controller}
    for qb in qubits.values():
        instruments[qb.drive.local_oscillator.name] = qb.drive.local_oscillator
        instruments[qb.readout.local_oscillator.name] = qb.readout.local_oscillator
        instruments[qb.twpa.local_oscillator.name] = qb.twpa.local_oscillator
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="2D",
    )
