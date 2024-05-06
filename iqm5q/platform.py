import itertools
import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import HDAWG, PQSC, SHFQC
from laboneq.simple import DeviceSetup
from qibolab import Platform
from qibolab.channel import AcquisitionChannelConfig
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.instruments.zhinst import (
    ZIChannel,
    ZIAcquisitionChannel,
    ZurichIQChannelConfig,
    ZurichDCChannelConfig,
    Zurich,
)
from qibolab.kernels import Kernels
from qibolab.serialize import (
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent

TWPA_ADDRESS = "192.168.0.35"

N_QUBITS = 5
N_COUPLERS = 4


def create():
    """IQM 5q-chip controlled Zurich Instruments SHFQC, HDAWGs and PQSC."""

    device_setup = DeviceSetup("EL_ZURO")
    # Dataserver
    device_setup.add_dataserver(host="localhost", port=8004)
    # Instruments
    device_setup.add_instruments(
        HDAWG("device_hdawg", address="DEV8660"),
        HDAWG("device_hdawg2", address="DEV8673"),
        PQSC("device_pqsc", address="DEV10055", reference_clock_source="internal"),
        SHFQC("device_shfqc", address="DEV12146"),
    )

    device_setup.add_connections(
        "device_pqsc",
        create_connection(to_instrument="device_hdawg2", ports="ZSYNCS/1"),
        create_connection(to_instrument="device_hdawg", ports="ZSYNCS/0"),
        create_connection(to_instrument="device_shfqc", ports="ZSYNCS/2"),
    )

    runcard = load_runcard(FOLDER)
    kernels = Kernels.load(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard, kernels)
    channel_configs = runcard["channels"]
    settings = load_settings(runcard)

    twpa_pump = SGS100A("TWPA", TWPA_ADDRESS)

    zi_channels = []
    for q in range(N_QUBITS):
        # acquisition. wire "L2-7"
        qubits[q].acquisition = ZIAcquisitionChannel(
            f"qubit_{q}/acquire",
            AcquisitionChannelConfig(**channel_configs[f"qubit_{q}/acquire"]),
            "device_shfqc",
            "[QACHANNELS/0/INPUT]",
            twpa_pump,
        )
        zi_channels.append(qubits[q].acquisition)
        # readout. wire "L3-31"
        qubits[q].readout = ZIChannel(
            f"qubit_{q}/measure",
            ZurichIQChannelConfig(**channel_configs[f"qubit_{q}/measure"]),
            "device_shfqc",
            "[QACHANNELS/0/OUTPUT]",
        )
        zi_channels.append(qubits[q].readout)
        # drive. wire f"L4-{15+q}"
        qubits[q].drive = ZIChannel(
            f"qubit_{q}/drive",
            ZurichIQChannelConfig(**channel_configs[f"qubit_{q}/drive"]),
            "device_shfqc",
            f"SGCHANNELS/{q}/OUTPUT",
        )
        zi_channels.append(qubits[q].drive)
        # flux qubits. wire f"L4-{6+q}"
        qubits[q].flux = ZIChannel(
            f"qubit_{q}/flux",
            ZurichDCChannelConfig(**channel_configs[f"qubit_{q}/flux"]),
            "device_hdawg",
            f"SIGOUTS/{q}",
        )
        zi_channels.append(qubits[q].flux)

    # coupler flux. wires f"L4-{i}" for i in range(11, 15)
    for c, i in zip(itertools.chain(range(0, 2), range(3, 4)), range(5, 8)):
        couplers[c].flux = ZIChannel(
            f"coupler_{c}/flux",
            ZurichDCChannelConfig(**channel_configs[f"coupler_{c}/flux"]),
            "device_hdawg",
            f"SIGOUTS/{i}",
        )
        zi_channels.append(couplers[c].flux)
    couplers[4].flux = ZIChannel(
        "coupler_4/flux",
        ZurichDCChannelConfig(**channel_configs["coupler_4/flux"]),
        "device_hdawg2",
        "SIGOUTS/0",
    )
    zi_channels.append(couplers[4].flux)

    controller = Zurich(
        "EL_ZURO",
        device_setup=device_setup,
        channels=zi_channels,
        time_of_flight=75,
        smearing=50,
    )

    instruments = {controller.name: controller}
    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="2D",
        couplers=couplers,
    )
