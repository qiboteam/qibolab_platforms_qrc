import pathlib

import networkx as nx
import yaml
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster import (
    Cluster,
    Cluster_Settings,
    ReferenceClockSource,
)
from qibolab.instruments.qblox.cluster_qcm_bb import ClusterQCM_BB
from qibolab.instruments.qblox.cluster_qcm_rf import ClusterQCM_RF
from qibolab.instruments.qblox.cluster_qrm_rf import ClusterQRM_RF
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

ADDRESS = "192.168.0.2"
TIME_OF_FLIGHT = 500
RUNCARD = pathlib.Path(__file__).parent / "tii1q_d28.yml"


def create(runcard_path=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    runcard = load_runcard(runcard_path)

    cluster = Cluster(
        name="cluster",
        address=ADDRESS,
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    )

    # DEBUG: debug folder = report folder
    # import os
    # folder = os.path.dirname(runcard) + "/debug/"
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
    # for name in modules:
    #     modules[name]._debug_folder = folder
    modules = {
        "qrm_rf0": ClusterQRM_RF("qrm_rf0", f"{ADDRESS}:15", cluster),
        "qcm_rf0": ClusterQRM_RF("qcm_rf0", f"{ADDRESS}:13", cluster),
    }

    controller = QbloxController("qblox_controller", cluster, modules)

    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-31r", port=modules["qrm_rf0"].ports["o1"])
    # Feedback
    channels |= Channel(name="L2-1", port=modules["qrm_rf0"].ports["i1"])
    # Drive
    channels |= Channel(name="L3-31d", port=modules["qcm_rf0"].ports["o1"])

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    settings = load_settings(runcard)

    return Platform(
        "tii1q_d28", qubits, pairs, instruments, settings, resonator_type="3D"
    )
