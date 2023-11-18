import pathlib

import networkx as nx
import yaml
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster import (
    Cluster,
    Cluster_Settings,
    ReferenceClockSource,
)
from qibolab.instruments.qblox.cluster_qcm_bb import (
    ClusterQCM_BB,
    ClusterQCM_BB_Settings,
)
from qibolab.instruments.qblox.cluster_qcm_rf import (
    ClusterQCM_RF,
    ClusterQCM_RF_Settings,
)
from qibolab.instruments.qblox.cluster_qrm_rf import (
    ClusterQRM_RF,
    ClusterQRM_RF_Settings,
)
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.qblox.port import (
    ClusterBB_OutputPort_Settings,
    ClusterRF_OutputPort_Settings,
    QbloxInputPort_Settings,
)
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "qblox"
ADDRESS = "192.168.0.6"
TIME_OF_FLIGHT = 500
RUNCARD = pathlib.Path(__file__).parent / "spinq10q.yml"

READOUT_ATTENUATION_FL1 = 40
READOUT_ATTENUATION_FL2 = 36
READOUT_GAIN = 0.5
DRIVE_ATTENUATION = 20
DRIVE_GAIN = 0.5
FLUX_GAIN = 0.5

instruments_settings = {
    "cluster": Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    "qrm_rf0": ClusterQRM_RF_Settings(  # q1, q2, q3, q4, q5
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-20",
                attenuation=READOUT_ATTENUATION_FL1,
                lo_frequency=7_385_000_000,
                gain=READOUT_GAIN,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L1-1",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=1800,
            ),
        }
    ),
    "qrm_rf1": ClusterQRM_RF_Settings(  # q6, q7, q8, q9, q10
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-21",
                attenuation=READOUT_ATTENUATION_FL2,
                lo_frequency=7_640_000_000,
                gain=READOUT_GAIN,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L2-17",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=1800,
            ),
        }
    ),
    "qcm_rf0": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L6-1",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_428_338_000,  # LOW_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
            "o2": ClusterRF_OutputPort_Settings(
                channel="L6-2",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=5_041_000_000,  # HIGH_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
        }
    ),
    "qcm_rf1": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L6-3",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_466_000_000,  # LOW_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
            "o2": ClusterRF_OutputPort_Settings(
                channel="L6-4",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=5_041_000_000,  # HIGH_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
        }
    ),
    "qcm_rf2": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L6-5",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_307_000_000,  # LOW_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
            "o2": ClusterRF_OutputPort_Settings(
                channel="L6-6",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_994_000_000,  # HIGH_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
        }
    ),
    "qcm_rf3": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L6-7",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_327_000_000,  # LOW_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
            "o2": ClusterRF_OutputPort_Settings(
                channel="L6-8",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_931_000_000,  # HIGH_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
        }
    ),
    "qcm_rf4": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L6-9",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_029_000_000,  # LOW_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
            "o2": ClusterRF_OutputPort_Settings(
                channel="L6-10",
                attenuation=DRIVE_ATTENUATION,
                lo_frequency=4_564_000_000,  # HIGH_FREQ_QUBIT_LO_FREQ,
                gain=DRIVE_GAIN,
            ),
        }
    ),
    "qcm_bb0": ClusterQCM_BB_Settings(
        {
            "o1": ClusterBB_OutputPort_Settings(
                channel="L6-39",
                gain=FLUX_GAIN,
                qubit=1,
            ),
            "o2": ClusterBB_OutputPort_Settings(
                channel="L6-40",
                gain=FLUX_GAIN,
                qubit=2,
            ),
            "o3": ClusterBB_OutputPort_Settings(
                channel="L6-41",
                gain=FLUX_GAIN,
                qubit=3,
            ),
            "o4": ClusterBB_OutputPort_Settings(
                channel="L6-42",
                gain=FLUX_GAIN,
                qubit=4,
            ),
        }
    ),
    "qcm_bb1": ClusterQCM_BB_Settings(
        {
            "o1": ClusterBB_OutputPort_Settings(
                channel="L6-43",
                gain=FLUX_GAIN,
                qubit=5,
            ),
            "o2": ClusterBB_OutputPort_Settings(
                channel="L6-44", gain=FLUX_GAIN, qubit=6
            ),
            "o3": ClusterBB_OutputPort_Settings(
                channel="L6-45",
                gain=FLUX_GAIN,
                qubit=7,
            ),
            "o4": ClusterBB_OutputPort_Settings(
                channel="L6-46",
                gain=FLUX_GAIN,
                qubit=8,
            ),
        }
    ),
    "qcm_bb2": ClusterQCM_BB_Settings(
        {
            "o1": ClusterBB_OutputPort_Settings(
                channel="L6-47",
                gain=FLUX_GAIN,
                qubit=9,
            ),
            "o2": ClusterBB_OutputPort_Settings(
                channel="L6-48",
                gain=FLUX_GAIN,
                qubit=10,
            ),
        }
    ),
}


def create(runcard_path=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    def instantiate_module(modules, cls, name, address, settings):
        module_settings = settings[name]
        modules[name] = cls(name=name, address=address, settings=module_settings)
        return modules[name]

    modules = {}

    cluster = Cluster(
        name="cluster",
        address="192.168.0.6",
        settings=instruments_settings["cluster"],
    )

    qrm_rf0 = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf0", "192.168.0.6:18", instruments_settings
    )  # qubits q1, q2, q3, q4, q5
    qrm_rf1 = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf1", "192.168.0.6:20", instruments_settings
    )  # qubits q6, q7, q8, q9, q10

    qcm_rf0 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf0", "192.168.0.6:8", instruments_settings
    )  # qubits q1, q2
    qcm_rf1 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf1", "192.168.0.6:10", instruments_settings
    )  # qubits q3, q4
    qcm_rf2 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf2", "192.168.0.6:12", instruments_settings
    )  # qubits q5, q6
    qcm_rf3 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf3", "192.168.0.6:14", instruments_settings
    )  # qubits q7, q8
    qcm_rf4 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf4", "192.168.0.6:16", instruments_settings
    )  # qubits q9, q10

    qcm_bb0 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb0", "192.168.0.6:2", instruments_settings
    )  # qubits q1, q2, q3, q4
    qcm_bb1 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb1", "192.168.0.6:4", instruments_settings
    )  # qubits q5, q6, q7, q8
    qcm_bb2 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb2", "192.168.0.6:6", instruments_settings
    )  # qubits q9, q10

    # DEBUG: debug folder = report folder
    import os
    from datetime import datetime

    QPU = "spinq10q"
    debug_folder = f"/home/users/alvaro.orgaz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)
    for name in modules:
        modules[name]._debug_folder = debug_folder

    controller = QbloxController("qblox_controller", cluster, modules)

    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    twpa_pump1 = SGS100A(name="twpa_pump1", address="192.168.0.39")

    # Create channel objects
    channels = {}
    # readout
    channels["L3-20"] = Channel(name="L3-20", port=qrm_rf0.ports["o1"])
    channels["L3-21"] = Channel(name="L3-21", port=qrm_rf1.ports["o1"])

    # feedback
    channels["L1-1"] = Channel(name="L1-1", port=qrm_rf0.ports["i1"])
    channels["L2-17"] = Channel(name="L2-17", port=qrm_rf1.ports["i1"])

    # drive
    channels["L6-1"] = Channel(name="L6-1", port=qcm_rf0.ports["o1"])
    channels["L6-2"] = Channel(name="L6-2", port=qcm_rf0.ports["o2"])
    channels["L6-3"] = Channel(name="L6-3", port=qcm_rf1.ports["o1"])
    channels["L6-4"] = Channel(name="L6-4", port=qcm_rf1.ports["o2"])
    channels["L6-5"] = Channel(name="L6-5", port=qcm_rf2.ports["o1"])
    channels["L6-6"] = Channel(name="L6-6", port=qcm_rf2.ports["o2"])
    channels["L6-7"] = Channel(name="L6-7", port=qcm_rf3.ports["o1"])
    channels["L6-8"] = Channel(name="L6-8", port=qcm_rf3.ports["o2"])
    channels["L6-9"] = Channel(name="L6-9", port=qcm_rf4.ports["o1"])
    channels["L6-10"] = Channel(name="L6-10", port=qcm_rf4.ports["o2"])

    # flux
    channels["L6-39"] = Channel(name="L6-39", port=qcm_bb0.ports["o1"])
    channels["L6-40"] = Channel(name="L6-40", port=qcm_bb0.ports["o2"])
    channels["L6-41"] = Channel(name="L6-41", port=qcm_bb0.ports["o3"])
    channels["L6-42"] = Channel(name="L6-42", port=qcm_bb0.ports["o4"])
    channels["L6-43"] = Channel(name="L6-43", port=qcm_bb1.ports["o1"])
    channels["L6-44"] = Channel(name="L6-44", port=qcm_bb1.ports["o2"])
    channels["L6-45"] = Channel(name="L6-45", port=qcm_bb1.ports["o3"])
    channels["L6-46"] = Channel(name="L6-46", port=qcm_bb1.ports["o4"])
    # channels["L6-47"] = Channel(name="L6-47", port=qcm_bb2.ports["o3"])
    # channels["L6-48"] = Channel(name="L6-48", port=qcm_bb2.ports["o4"])
    channels["L6-47"] = Channel(name="L6-47", port=None)
    channels["L6-48"] = Channel(name="L6-48", port=None)

    # TWPA
    channels["L3-10"] = Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump0
    channels["L3-23"] = Channel(name="L3-23", port=None)
    channels["L3-23"].local_oscillator = twpa_pump1

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)
    # remove witness qubit
    # del qubits[5]
    # assign channels to qubits
    for q in [1, 2, 3, 4, 5]:
        qubits[q].readout = channels["L3-20"]
        qubits[q].feedback = channels["L1-1"]
        qubits[q].twpa = channels["L3-10"]
    for q in [6, 7, 8, 9, 10]:
        qubits[q].readout = channels["L3-21"]
        qubits[q].feedback = channels["L2-17"]
        qubits[q].twpa = channels["L3-23"]

    for q in range(1, 11):
        qubits[q].drive = channels[f"L6-{q}"]
        qubits[q].flux = channels[f"L6-{38+q}"]
        channels[f"L6-{38+q}"].qubit = qubits[q]
        # set maximum allowed bias
        qubits[q].flux.max_bias = 2.5

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
        twpa_pump1.name: twpa_pump1,
    }
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        "spinq10q_qblox", qubits, pairs, instruments, settings, resonator_type="2D"
    )
