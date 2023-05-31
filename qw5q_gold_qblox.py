import pathlib
import networkx as nx

from qibolab.platform import Platform
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.qblox.channel import QbloxChannel
from qibolab.instruments.qblox.cluster import Cluster, ClusterQRM_RF, ClusterQCM_RF, ClusterQCM
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.channels import Channel, ChannelMap

RUNCARD = pathlib.Path(__file__).parent / "qw5q_gold_qblox.yml"


def create(runcard=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard (str): Path to the runcard file.
    """

    

    modules = {}
    cluster = modules["cluster"] = Cluster(name="cluster", address="192.168.0.6")

    qrm_rf_a = modules["qrm_rf_a"] = ClusterQRM_RF(name="qrm_rf_a", address="192.168.0.6:10") # qubits q0, q1, q5
    qrm_rf_b = modules["qrm_rf_b"] = ClusterQRM_RF(name="qrm_rf_b", address="192.168.0.6:12") # qubits q2, q3, q4
    
    qcm_rf0 = modules["qcm_rf0"] = ClusterQCM_RF(name="qcm_rf0", address="192.168.0.6:8") # qubit q0
    qcm_rf1 = modules["qcm_rf1"] = ClusterQCM_RF(name="qcm_rf1", address="192.168.0.6:3") # qubits q1, q2
    qcm_rf2 = modules["qcm_rf2"] = ClusterQCM_RF(name="qcm_rf2", address="192.168.0.6:4") # qubits q3, q4

    qcm_bb0 = modules["qcm_bb1"] = ClusterQCM(name="qcm_bb1", address="192.168.0.6:5") # qubit q0
    qcm_bb1 = modules["qcm_bb0"] = ClusterQCM(name="qcm_bb0", address="192.168.0.6:2") # qubits q1, q2, q3, q4

    instruments = {}
    controller = instruments["controller"] = QbloxController("qblox_controller", modules)
    twpa_pump = instruments["twpa_pump"] = SGS100A(name="twpa_pump", address="192.168.0.37")

    # Create channel objects
    channels = {}
    # readout
    channels["L3-25_a"] = QbloxChannel(name="L3-25_a", instrument=qrm_rf_a, port_name="o1")
    channels["L3-25_b"] = QbloxChannel(name="L3-25_b", instrument=qrm_rf_b, port_name="o1")

    # feedback
    channels["L3-25_a"] = QbloxChannel(name="L2-5_a", instrument=qrm_rf_a, port_name="i1")
    channels["L3-25_b"] = QbloxChannel(name="L2-5_b", instrument=qrm_rf_b, port_name="i1")

    # drive
    channels["L3-15"] = QbloxChannel(name="L3-15", instrument=qcm_rf0, port_name="o1")
    channels["L3-11"] = QbloxChannel(name="L3-11", instrument=qcm_rf1, port_name="o1")
    channels["L3-12"] = QbloxChannel(name="L3-12", instrument=qcm_rf1, port_name="o2")
    channels["L3-13"] = QbloxChannel(name="L3-13", instrument=qcm_rf2, port_name="o1")
    channels["L3-14"] = QbloxChannel(name="L3-14", instrument=qcm_rf2, port_name="o2")

    # flux
    channels["L4-5"] = QbloxChannel(name="L4-5", instrument=qcm_bb0, port_name = "o1")
    channels["L4-1"] = QbloxChannel(name="L4-1", instrument=qcm_bb1, port_name = "o1")
    channels["L4-2"] = QbloxChannel(name="L4-2", instrument=qcm_bb1, port_name = "o2")
    channels["L4-3"] = QbloxChannel(name="L4-3", instrument=qcm_bb1, port_name = "o3")
    channels["L4-4"] = QbloxChannel(name="L4-4", instrument=qcm_bb1, port_name = "o4")

    # TWPA
    channels["L4-26"] = QbloxChannel(name="L4-4", instrument=twpa_pump)

    platform = Platform(name="qw5q_gold_qblox", runcard=runcard, instruments=instruments, channels=channels)

    # assign channels to qubits
    qubits = platform.qubits
    for q in [0, 1, 5]:
        qubits[q].readout = channels["L3-25_a"]
        qubits[q].feedback = channels["L2-5_a"]
        qubits[q].twpa = channels["L4-26"]
    for q in [2, 3, 4]:
        qubits[q].readout = channels["L3-25_b"]
        qubits[q].feedback = channels["L2-5_b"]
        qubits[q].twpa = channels["L4-26"]

    qubits[0].drive = channels["L3-15"]
    qubits[0].flux = channels["L4-5"]
    channels["L4-5"].qubit = qubits[0]
    for q in range(1, 5):
        qubits[q].drive = channels[f"L3-{10 + q}"]
        qubits[q].flux = channels[f"L4-{q}"]
        channels[f"L4-{q}"].qubit = qubits[q]

    # set maximum allowed bias
    for q in range(5):
        platform.qubits[q].flux.max_bias = 2.5
    # Platfom topology
    
    Q = [f"q{i}" for i in range(5)]
    chip = nx.Graph()
    chip.add_nodes_from(Q)
    graph_list = [
        (Q[0], Q[2]),
        (Q[1], Q[2]),
        (Q[3], Q[2]),
        (Q[4], Q[2]),
    ]
    chip.add_edges_from(graph_list)
    platform.topology = chip

    return platform