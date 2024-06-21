import pathlib

from laboneq.dsl.device import create_connection
from laboneq.dsl.device.instruments import HDAWG, PQSC, SHFQC
from laboneq.simple import DeviceSetup
from qibolab import Platform
from qibolab.components import AcquireChannel, DcChannel, IqChannel, OscillatorConfig
from qibolab.instruments.zhinst import (
    ZiAcquisitionConfig,
    ZiChannel,
    ZiDcConfig,
    ZiIqConfig,
    Zurich,
)
from qibolab.serialize import (
    load_component_config,
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent

N_QUBITS = 2


def create():
    """Tii 2q chip"""

    device_setup = DeviceSetup()
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
    settings = load_settings(runcard)

    components = {}
    drive_lo = "qubit_1_2/drive/lo"
    measure_lo = "qubit_1_2/measure/lo"
    components[drive_lo] = load_component_config(runcard, drive_lo, OscillatorConfig)
    components[measure_lo] = load_component_config(runcard, measure_lo, OscillatorConfig)
    zi_channels = []
    for q in range(N_QUBITS):
        measure_name = f"qubit_{q}/measure"
        acquisition_name = f"qubit_{q}/acquire"
        components[acquisition_name] = load_component_config(runcard, acquisition_name, ZiAcquisitionConfig)
        qubits[q].acquisition = AcquireChannel(
            name=acquisition_name,
            twpa_pump=None,
            measure=measure_name,
        )
        zi_channels.append(ZiChannel(qubits[q].acquisition, device="device_shfqc", path="QACHANNELS/0/INPUT"))

        components[measure_name] = load_component_config(runcard, measure_name, ZiIqConfig)
        qubits[q].measure = IqChannel(
            name=measure_name,
            lo=measure_lo,
            mixer=None,
            acquisition=acquisition_name
        )
        zi_channels.append(ZiChannel(qubits[q].measure, device="device_shfqc", path="QACHANNELS/0/OUTPUT"))

        drive_name = f"qubit_{q}/drive"
        components[drive_name] = load_component_config(runcard, drive_name, ZiIqConfig)
        qubits[q].drive = IqChannel(
            name=drive_name,
            mixer=None,
            lo=drive_lo,
        )
        zi_channels.append(ZiChannel(qubits[q].drive, device="device_shfqc", path=f"SGCHANNELS/{q}/OUTPUT"))

    flux_name = "qubit_1/flux"
    components[flux_name] = load_component_config(runcard, flux_name, ZiDcConfig)
    qubits[1].flux = DcChannel(
        name=flux_name,
    )
    zi_channels.append(ZiChannel(qubits[1].flux, device="device_hdawg", path="SIGOUTS/0"))

    controller = Zurich(
        "ZURO_BLANCO",
        device_setup=device_setup,
        channels=zi_channels,
        time_of_flight=75,
        smearing=50,
    )

    instruments = {controller.name: controller}
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER),
        qubits,
        pairs,
        components,
        instruments,
        settings,
        resonator_type="3D",
        couplers={},
    )
