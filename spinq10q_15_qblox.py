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

NAME = "spinq10q_15_qblox"
ADDRESS = "192.168.0.6"
RUNCARD = pathlib.Path(__file__).parent / "spinq10q_15.yml"


def create(runcard_path=RUNCARD):
    """SpinQ 10q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """

    runcard = load_runcard(runcard_path)
    cluster = Cluster(
        name="cluster",
        address="192.168.0.6",
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    )
    modules = {
        "qrm_rf0": ClusterQRM_RF(
            "qrm_rf0", f"{ADDRESS}:20", cluster
        ),  # qubits q1, q2, q3, q4, q5
        "qcm_rf0": ClusterQCM_RF("qcm_rf0", f"{ADDRESS}:8", cluster),  # qubits q1, q2
        "qcm_rf1": ClusterQCM_RF("qcm_rf1", f"{ADDRESS}:10", cluster),  # qubits q3, q4
        "qcm_rf2": ClusterQCM_RF("qcm_rf2", f"{ADDRESS}:12", cluster),  # qubits q5, q6
        "qcm_bb0": ClusterQCM_BB(
            "qcm_bb0", f"{ADDRESS}:2", cluster
        ),  # qubits q1, q2, q3, q4
        "qcm_bb1": ClusterQCM_BB(
            "qcm_bb1", f"{ADDRESS}:4", cluster
        ),  # qubits q5, q6, q7, q8
    }
    controller = QbloxController("qblox_controller", cluster, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # DEBUG: debug folder = report folder
    import os
    from datetime import datetime

    QPU = "spinq10q"
    debug_folder = f"/home/users/alvaro.orgaz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)
    for name in modules:
        modules[name]._debug_folder = debug_folder

    # Create channel objects
    channels = {}
    # readout
    channels["L3-20"] = Channel(name="L3-20", port=modules["qrm_rf0"].ports["o1"])

    # feedback
    channels["L1-1"] = Channel(name="L1-1", port=modules["qrm_rf0"].ports["i1"])

    # drive
    channels["L6-1"] = Channel(name="L6-1", port=modules["qcm_rf0"].ports["o1"])
    channels["L6-2"] = Channel(name="L6-2", port=modules["qcm_rf0"].ports["o2"])
    channels["L6-3"] = Channel(name="L6-3", port=modules["qcm_rf1"].ports["o1"])
    channels["L6-4"] = Channel(name="L6-4", port=modules["qcm_rf1"].ports["o2"])
    channels["L6-5"] = Channel(name="L6-5", port=modules["qcm_rf2"].ports["o1"])

    # flux
    channels["L6-39"] = Channel(name="L6-39", port=modules["qcm_bb0"].ports["o1"])
    channels["L6-40"] = Channel(name="L6-40", port=modules["qcm_bb0"].ports["o2"])
    channels["L6-41"] = Channel(name="L6-41", port=modules["qcm_bb0"].ports["o3"])
    channels["L6-42"] = Channel(name="L6-42", port=modules["qcm_bb0"].ports["o4"])
    channels["L6-43"] = Channel(name="L6-43", port=modules["qcm_bb1"].ports["o1"])

    # TWPA
    channels["L3-10"] = Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump0

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    for q in [1, 2, 3, 4, 5]:
        qubits[q].readout = channels["L3-20"]
        qubits[q].feedback = channels["L1-1"]
        qubits[q].twpa = channels["L3-10"]

    for q in range(1, 6):
        qubits[q].drive = channels[f"L6-{q}"]
        qubits[q].flux = channels[f"L6-{38+q}"]
        channels[f"L6-{38+q}"].qubit = qubits[q]
        # set maximum allowed bias
        qubits[q].flux.max_bias = 2.5

    settings = load_settings(runcard)

    return Platform(
        "spinq10q_15_qblox", qubits, pairs, instruments, settings, resonator_type="2D"
    )
