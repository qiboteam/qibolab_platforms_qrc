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
from qibolab.instruments.qblox.port import QbloxOutputPort
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "tii2q2_cavity_qblox"
ADDRESS = "192.168.0.2"
RUNCARD = pathlib.Path(__file__).parent / "tii2q_cavity.yml"


def create(runcard_path=RUNCARD):
    """TII 2q-chip in a 3D cavity controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    runcard = load_runcard(runcard_path)
    cluster = Cluster(
        name="cluster",
        address="192.168.0.2",
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    )
    modules = {
        "qrm_rf": ClusterQRM_RF(
            "qrm_rf", f"{ADDRESS}:13", cluster
        ),  # qubits q1, q2 readout
        "qcm_rf": ClusterQRM_RF(
            "qcm_rf", f"{ADDRESS}:15", cluster
        ),  # qubits q1, q2 drive
    }
    controller = QbloxController("qblox_controller", cluster, modules)
    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # DEBUG: debug folder = report folder
    import os
    from datetime import datetime

    QPU = "tii2q_cavity"
    debug_folder = f"/home/users/alvaro.orgaz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)
    for name in modules:
        modules[name]._debug_folder = debug_folder

    # Create channel objects
    channels = {}
    # readout
    channels["w4r"] = Channel(name="w4r", port=modules["qrm_rf"].ports["o1"])

    # feedback
    channels["v2"] = Channel(name="v2", port=modules["qrm_rf"].ports["i1"])

    # drive
    channels["w4d"] = Channel(name="w4d", port=modules["qcm_rf"].ports["o1"])

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    for q in [1, 2]:
        qubits[q].readout = channels["w4r"]
        qubits[q].feedback = channels["v2"]
        qubits[q].drive = channels["w4d"]
        # qubits[q].flux = None

    settings = load_settings(runcard)

    return Platform(
        "tii2q2_cavity_qblox", qubits, pairs, instruments, settings, resonator_type="3D"
    )
