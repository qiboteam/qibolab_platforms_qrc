import pathlib
import networkx as nx
import yaml

from qibolab.platform import Platform
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.qblox.channel import QbloxChannel
from qibolab.instruments.qblox.cluster import Cluster
from qibolab.instruments.qblox.cluster_qrm_rf import ClusterQRM_RF
from qibolab.instruments.qblox.cluster_qcm_rf import ClusterQCM_RF
from qibolab.instruments.qblox.cluster_qcm_bb import ClusterQCM_BB
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.channels import Channel, ChannelMap

RUNCARD = pathlib.Path(__file__).parent / "qw5q_gold_qblox.yml"


def create(runcard=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard (str): Path to the runcard file.
    """

    with open(runcard) as file:
        instruments_settings = yaml.safe_load(file)
    
    def instantiate_module(modules, cls, name, address, settings):
        module_settings = settings["instruments"][name]["settings"]
        modules[name] = cls(name=name, address=address, settings=module_settings)
        return modules[name]
    
    modules = {}

    cluster  = Cluster(name="cluster", address="192.168.0.6", settings=instruments_settings["instruments"]["cluster"]["settings"])
    
    qrm_rf_a = instantiate_module(modules, ClusterQRM_RF, "qrm_rf_a", "192.168.0.6:10", instruments_settings) # qubits q0, q1, q5
    qrm_rf_b = instantiate_module(modules, ClusterQRM_RF, "qrm_rf_b", "192.168.0.6:12", instruments_settings) # qubits q2, q3, q4
    
    qcm_rf0  = instantiate_module(modules, ClusterQCM_RF, "qcm_rf0", "192.168.0.6:8", instruments_settings) # qubit q0
    qcm_rf1  = instantiate_module(modules, ClusterQCM_RF, "qcm_rf1", "192.168.0.6:3", instruments_settings) # qubits q1, q2
    qcm_rf2  = instantiate_module(modules, ClusterQCM_RF, "qcm_rf2", "192.168.0.6:4", instruments_settings) # qubits q3, q4
    
    qcm_bb0  = instantiate_module(modules, ClusterQCM_BB, "qcm_bb0", "192.168.0.6:5", instruments_settings) # qubit q0
    qcm_bb1  = instantiate_module(modules, ClusterQCM_BB, "qcm_bb1", "192.168.0.6:2", instruments_settings) # qubits q1, q2, q3, q4

    
    # DEBUG: debug folder = report folder
    import os
    folder = os.path.dirname(runcard) + "/debug/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    for name in modules:
        modules[name]._debug_folder = folder


    controller = QbloxController("qblox_controller", cluster, modules)

    twpa_pump = SGS100A(name="twpa_pump", address="192.168.0.37")
    twpa_pump.frequency = instruments_settings["instruments"]["twpa_pump"]["settings"]["frequency"]
    twpa_pump.power = instruments_settings["instruments"]["twpa_pump"]["settings"]["power"]
    
    instruments = [controller, twpa_pump]
    
    # Create channel objects
    channels = {}
    # readout
    channels["L3-25_a"] = QbloxChannel(name="L3-25_a", instrument=qrm_rf_a, port_name="o1")
    channels["L3-25_b"] = QbloxChannel(name="L3-25_b", instrument=qrm_rf_b, port_name="o1")

    # feedback
    channels["L2-5_a"] = QbloxChannel(name="L2-5_a", instrument=qrm_rf_a, port_name="i1")
    channels["L2-5_b"] = QbloxChannel(name="L2-5_b", instrument=qrm_rf_b, port_name="i1")

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