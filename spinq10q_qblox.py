import pathlib

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

NAME = "qblox"
ADDRESS = "192.168.0.6"
RUNCARD = pathlib.Path(__file__).parent / "spinq10q.yml"


def create(runcard_path=RUNCARD):
    """SpinQ 10q-chip controlled using qblox cluster 6.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(runcard_path)
    cluster = Cluster(
        name="cluster",
        address="192.168.0.6",
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.EXTERNAL),
    )
    modules = {
        "qrm_rf0": ClusterQRM_RF(
            "qrm_rf0", f"{ADDRESS}:19", cluster
        ),  # qubits q1, q2, q3, q4, q5
        "qrm_rf1": ClusterQRM_RF(
            "qrm_rf1", f"{ADDRESS}:20", cluster
        ),  # qubits q6, q7, q8, q9, q10
        "qcm_rf0": ClusterQCM_RF("qcm_rf0", f"{ADDRESS}:8", cluster),  # qubits q1, q2
        "qcm_rf1": ClusterQCM_RF("qcm_rf1", f"{ADDRESS}:10", cluster),  # qubits q3, q4
        "qcm_rf2": ClusterQCM_RF("qcm_rf2", f"{ADDRESS}:12", cluster),  # qubits q5, q6
        "qcm_rf3": ClusterQCM_RF("qcm_rf3", f"{ADDRESS}:14", cluster),  # qubits q7, q8
        "qcm_rf4": ClusterQCM_RF("qcm_rf4", f"{ADDRESS}:16", cluster),  # qubits q9, q10
        "qcm_bb0": ClusterQCM_BB(
            "qcm_bb0", f"{ADDRESS}:2", cluster
        ),  # qubits q1, q2, q3, q4
        "qcm_bb1": ClusterQCM_BB(
            "qcm_bb1", f"{ADDRESS}:4", cluster
        ),  # qubits q5, q6, q7, q8
        "qcm_bb2": ClusterQCM_BB("qcm_bb2", f"{ADDRESS}:6", cluster),  # qubits q9, q10
    }
    controller = QbloxController("qblox_controller", cluster, modules)
    twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    twpa_pump1 = SGS100A(name="twpa_pump1", address="192.168.0.39")

    instruments = {
        controller.name: controller,
        twpa_pump0.name: twpa_pump0,
        twpa_pump1.name: twpa_pump1,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # DEBUG: debug folder = report folder ###################################################################
    # import os
    # from datetime import datetime

    # QPU = "spinq10q"
    # debug_folder = f"/home/users/alvaro.orgaz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    # if not os.path.exists(debug_folder):
    #     os.makedirs(debug_folder)
    # for name in modules:
    #     modules[name]._debug_folder = debug_folder
    #########################################################################################################

    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-20", port=modules["qrm_rf0"].ports["o1"])
    channels |= Channel(name="L3-21", port=modules["qrm_rf1"].ports["o1"])
    # Feedback
    channels |= Channel(name="L1-1", port=modules["qrm_rf0"].ports["i1"])
    channels |= Channel(name="L2-17", port=modules["qrm_rf1"].ports["i1"])
    # Drive
    channels |= Channel(name="L6-1", port=modules["qcm_rf0"].ports["o1"])
    channels |= Channel(name="L6-2", port=modules["qcm_rf0"].ports["o2"])
    channels |= Channel(name="L6-3", port=modules["qcm_rf1"].ports["o1"])
    channels |= Channel(name="L6-4", port=modules["qcm_rf1"].ports["o2"])
    channels |= Channel(name="L6-5", port=modules["qcm_rf2"].ports["o1"])
    channels |= Channel(name="L6-6", port=modules["qcm_rf2"].ports["o2"])
    channels |= Channel(name="L6-7", port=modules["qcm_rf3"].ports["o1"])
    channels |= Channel(name="L6-8", port=modules["qcm_rf3"].ports["o2"])
    channels |= Channel(name="L6-9", port=modules["qcm_rf4"].ports["o1"])
    channels |= Channel(name="L6-10", port=modules["qcm_rf4"].ports["o2"])
    # Flux
    channels |= Channel(name="L6-39", port=modules["qcm_bb0"].ports["o1"])
    channels |= Channel(name="L6-40", port=modules["qcm_bb0"].ports["o2"])
    channels |= Channel(name="L6-41", port=modules["qcm_bb0"].ports["o3"])
    channels |= Channel(name="L6-42", port=modules["qcm_bb0"].ports["o4"])
    channels |= Channel(name="L6-43", port=modules["qcm_bb1"].ports["o1"])
    channels |= Channel(name="L6-44", port=modules["qcm_bb1"].ports["o2"])
    channels |= Channel(name="L6-45", port=modules["qcm_bb1"].ports["o3"])
    channels |= Channel(name="L6-46", port=modules["qcm_bb1"].ports["o4"])
    channels |= Channel(name="L6-47", port=modules["qcm_bb2"].ports["o4"])
    channels |= Channel(name="L6-48", port=modules["qcm_bb2"].ports["o3"])

    # TWPA
    channels |= Channel(name="L3-10", port=None)
    channels["L3-10"].local_oscillator = twpa_pump0
    channels |= Channel(name="L3-23", port=None)
    channels["L3-23"].local_oscillator = twpa_pump1

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

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

    settings = load_settings(runcard)

    return Platform(
        "spinq10q_qblox", qubits, pairs, instruments, settings, resonator_type="2D"
    )
