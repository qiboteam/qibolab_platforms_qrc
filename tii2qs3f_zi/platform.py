import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import HDAWG, PQSC, SHFQC
from laboneq.simple import DeviceSetup
from qibolab import Platform
from qibolab.instruments.zhinst import (
    ZiAcquisitionChannel,
    ZiAcquisitionConfig,
    ZiChannel,
    ZiDcConfig,
    ZiIqConfig,
    Zurich,
)
from qibolab.serialize import (
    load_channel_configs,
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
        "device_pqsc",
        create_connection(to_instrument="device_hdawg", ports="ZSYNCS/0"),
        create_connection(to_instrument="device_shfqc", ports="ZSYNCS/2"),
    )

    runcard = load_runcard(FOLDER)
    qubits, _, pairs = load_qubits(runcard)
    channel_configs = load_channel_configs(runcard)
    settings = load_settings(runcard)

    channels = []
    for q in range(N_QUBITS):
        qubits[q].acquisition = ZiAcquisitionChannel(
            f"qubit_{q}/acquire",
            ZiAcquisitionConfig(**channel_configs[f"qubit_{q}/acquire"]),
            "device_shfqc",
            "QACHANNELS/0/INPUT",
            None,
        )
        channels.append(qubits[q].acquisition)

        qubits[q].readout = ZiChannel(
            f"qubit_{q}/measure",
            ZiIqConfig(**channel_configs[f"qubit_{q}/measure"]),
            "device_shfqc",
            "QACHANNELS/0/OUTPUT",
        )
        channels.append(qubits[q].readout)

        qubits[q].drive = ZiChannel(
            f"qubit_{q}/drive",
            ZiIqConfig(**channel_configs[f"qubit_{q}/drive"]),
            "device_shfqc",
            f"SGCHANNELS/{q}/OUTPUT",
        )
        channels.append(qubits[q].drive)

    qubits[1].flux = ZiChannel(
        "qubit_1/flux",
        ZiDcConfig(**channel_configs["qubit_1/flux"]),
        "device_hdawg",
        "SIGOUTS/0",
    )
    channels.append(qubits[1].flux)

    controller = Zurich(
        "EL_ZURO",
        device_setup=device_setup,
        channels=channels,
        time_of_flight=75,
        smearing=50,
    )

    instruments = {controller.name: controller}
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="3D",
        couplers={},
    )
