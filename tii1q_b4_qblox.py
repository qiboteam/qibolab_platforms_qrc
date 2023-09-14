import pathlib

import networkx as nx
import yaml
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster import (
    Cluster,
    Cluster_Settings,
    ReferenceClockSource,
)
from qibolab.instruments.qblox.cluster_qrm_rf import (
    ClusterQRM_RF,
    ClusterQRM_RF_Settings,
)
from qibolab.instruments.qblox.cluster_qcm_rf import (
    ClusterQCM_RF,
    ClusterQCM_RF_Settings,
)
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.qblox.port import (
    ClusterRF_OutputPort_Settings,
    QbloxInputPort_Settings,
)
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.instruments.erasynth import ERA
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings

NAME = "tii1qb4_qblox"
ADDRESS = "192.168.0.20"
TIME_OF_FLIGHT = 500
RUNCARD = pathlib.Path(__file__).parent / "tii1q_b4_qblox.yml"
TWPA_ADDRESS = "192.168.0.208"

instruments_settings = {
    "cluster": Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    "qrm_rf_a": ClusterQRM_RF_Settings(  # q0,q1,q5
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-21_a",
                attenuation=0,  # 38
                lo_frequency=7_255_000_000,
                gain=1,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L1-01",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=900,
            ),
        }
    ),
    "qrm_rf_b": ClusterQCM_RF_Settings(  # q2,q3,q4
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-21_b",
                attenuation=32,
                lo_frequency=7_850_000_000,
                gain=0.6,
            ),
        }
    ),
    "twpa_pump": {"frequency": 6_690_000_000, "power": -5.6},
}


def create(runcard_path=RUNCARD):
    """TII 1q-chip controlled using qblox cluster.

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
        address=ADDRESS,
        settings=instruments_settings["cluster"],
    )

    qrm_rf_a = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_a", "192.168.0.20:16", instruments_settings
    )  # qubits q0
    qrm_rf_b = instantiate_module(
        modules, ClusterQCM_RF, "qrm_rf_b", "192.168.0.20:12", instruments_settings
    )  # qubits q0

    # DEBUG: debug folder = report folder
    # import os
    # folder = os.path.dirname(runcard) + "/debug/"
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
    # for name in modules:
    #     modules[name]._debug_folder = folder

    controller = QbloxController("qblox_controller", cluster, modules)

    twpa_pump = ERA(name="twpa_pump", address=TWPA_ADDRESS)
    twpa_pump.frequency = instruments_settings["twpa_pump"]["frequency"]
    twpa_pump.power = instruments_settings["twpa_pump"]["power"]

    instruments = [controller, twpa_pump]

    # Create channel objects
    channels = {}
    # readout
    channels["L3-21_a"] = Channel(name="L3-21_a", port=qrm_rf_a.ports["o1"])
   

    # feedback
    channels["L1-01"] = Channel(name="L1-01", port=qrm_rf_a.ports["i1"])

    # drive
    channels["L3-21_b"] = Channel(name="L3-21_b", port=qrm_rf_b.ports["o1"])


    # flux (no flux tunable the tii1q_b4)

    # TWPA
    channels["L4-26"] = Channel(name="L4-4", port=None)
    channels["L4-26"].local_oscillator = twpa_pump

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)
    # remove witness qubit
    # del qubits[5]
    # assign channels to qubits
    
    qubits[0].readout = channels["L3-21_a"]
    qubits[0].feedback = channels["L1-01"]
    qubits[0].twpa = channels["L4-26"]
    qubits[0].drive = channels["L3-21_b"]

    instruments = {controller.name: controller, twpa_pump.name: twpa_pump}
    settings = load_settings(runcard)
    return Platform(
        "tii1qb4_qblox", qubits, pairs, instruments, settings, resonator_type="3D"
    )
