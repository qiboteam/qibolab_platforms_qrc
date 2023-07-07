import pathlib

import networkx as nx
import yaml
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster import Cluster
from qibolab.instruments.qblox.cluster_qcm_bb import ClusterQCM_BB
from qibolab.instruments.qblox.cluster_qcm_rf import ClusterQCM_RF
from qibolab.instruments.qblox.cluster_qrm_rf import ClusterQRM_RF
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform

NAME = "qblox"
ADDRESS = "192.168.0.6"
TIME_OF_FLIGHT = 500
RUNCARD = pathlib.Path(__file__).parent / "qw5q_gold.yml"

instruments_settings = {
    "cluster": {"settings": {"reference_clock_source": "internal"}},
    "qrm_rf_a": {
        "settings": {
            "ports": {
                "o1": {
                    "channel": "L3-25_a",
                    "attenuation": 38,
                    "lo_enabled": True,
                    "lo_frequency": 7_255_000_000,
                    "gain": 0.6,
                },
                "i1": {
                    "channel": "L2-5_a",
                    "acquisition_hold_off": TIME_OF_FLIGHT,
                    "acquisition_duration": 900,
                },
            },
            # 'classification_parameters': {
            #     0: {'rotation_angle':  99.758, 'threshold': 0.003933},
            #     1: {'rotation_angle': 146.297, 'threshold': 0.003488}
            # }
        }
    },
    "qrm_rf_b": {
        "settings": {
            "ports": {
                "o1": {
                    "channel": "L3-25_b",
                    "attenuation": 32,
                    "lo_enabled": True,
                    "lo_frequency": 7_850_000_000,
                    "gain": 0.6,
                },
                "i1": {
                    "channel": "L2-5_b",
                    "acquisition_hold_off": TIME_OF_FLIGHT,
                    "acquisition_duration": 900,
                },
            },
            # 'classification_parameters': {
            #     2: {'rotation_angle': 97.821, 'threshold': 0.002904},
            #     3: {'rotation_angle': 91.209, 'threshold': 0.004318},
            #     4: {'rotation_angle': 7.997, 'threshold': 0.002323}
            # }
        }
    },
    "qcm_rf0": {
        "settings": {
            "ports": {
                "o1": {
                    "channel": "L3-15",
                    "attenuation": 20,
                    "lo_enabled": True,
                    "lo_frequency": 5_250_304_836,
                    "gain": 0.470,
                }
            }
        }
    },
    "qcm_rf1": {
        "settings": {
            "ports": {
                "o1": {
                    "channel": "L3-11",
                    "attenuation": 20,
                    "lo_enabled": True,
                    "lo_frequency": 5_052_833_073,
                    "gain": 0.570,
                },
                "o2": {
                    "channel": "L3-12",
                    "attenuation": 20,
                    "lo_enabled": True,
                    "lo_frequency": 5_995_371_914,
                    "gain": 0.655,
                },
            }
        }
    },
    "qcm_rf2": {
        "settings": {
            "ports": {
                "o1": {
                    "channel": "L3-13",
                    "attenuation": 20,
                    "lo_enabled": True,
                    "lo_frequency": 6_961_018_001,
                    "gain": 0.550,
                },
                "o2": {
                    "channel": "L3-14",
                    "attenuation": 20,
                    "lo_enabled": True,
                    "lo_frequency": 6_786_543_060,
                    "gain": 0.596,
                },
            }
        }
    },
    "qcm_bb0": {
        "settings": {
            "ports": {
                "o1": {"channel": "L4-5", "gain": 0.5, "offset": 0.5507, "qubit": 0}
            }
        }
    },
    "qcm_bb1": {
        "settings": {
            "ports": {
                "o1": {"channel": "L4-1", "gain": 0.5, "offset": 0.2227, "qubit": 1},
                "o2": {"channel": "L4-2", "gain": 0.5, "offset": -0.3780, "qubit": 2},
                "o3": {"channel": "L4-3", "gain": 0.5, "offset": -0.8899, "qubit": 3},
                "o4": {"channel": "L4-4", "gain": 0.5, "offset": 0.5890, "qubit": 4},
            }
        }
    },
    "twpa_pump": {"settings": {"frequency": 6_535_900_000, "power": 4}},
}


def create(runcard=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard (str): Path to the runcard file.
    """

    def instantiate_module(modules, cls, name, address, settings):
        module_settings = settings[name]["settings"]
        modules[name] = cls(name=name, address=address, settings=module_settings)
        return modules[name]

    modules = {}

    cluster = Cluster(
        name="cluster",
        address="192.168.0.6",
        settings=instruments_settings["cluster"]["settings"],
    )

    qrm_rf_a = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_a", "192.168.0.6:10", instruments_settings
    )  # qubits q0, q1, q5
    qrm_rf_b = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_b", "192.168.0.6:12", instruments_settings
    )  # qubits q2, q3, q4

    qcm_rf0 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf0", "192.168.0.6:8", instruments_settings
    )  # qubit q0
    qcm_rf1 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf1", "192.168.0.6:3", instruments_settings
    )  # qubits q1, q2
    qcm_rf2 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf2", "192.168.0.6:4", instruments_settings
    )  # qubits q3, q4

    qcm_bb0 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb0", "192.168.0.6:5", instruments_settings
    )  # qubit q0
    qcm_bb1 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb1", "192.168.0.6:2", instruments_settings
    )  # qubits q1, q2, q3, q4

    # DEBUG: debug folder = report folder
    # import os
    # folder = os.path.dirname(runcard) + "/debug/"
    # if not os.path.exists(folder):
    #     os.makedirs(folder)
    # for name in modules:
    #     modules[name]._debug_folder = folder

    controller = QbloxController("qblox_controller", cluster, modules)

    twpa_pump = SGS100A(name="twpa_pump", address="192.168.0.37")
    twpa_pump.frequency = instruments_settings["twpa_pump"]["settings"]["frequency"]
    twpa_pump.power = instruments_settings["twpa_pump"]["settings"]["power"]

    instruments = [controller, twpa_pump]

    # Create channel objects
    channels = {}
    # readout
    channels["L3-25_a"] = Channel(name="L3-25_a", port=qrm_rf_a.ports["o1"])
    channels["L3-25_b"] = Channel(name="L3-25_b", port=qrm_rf_b.ports["o1"])

    # feedback
    channels["L2-5_a"] = Channel(name="L2-5_a", port=qrm_rf_a.ports["i1"])
    channels["L2-5_b"] = Channel(name="L2-5_b", port=qrm_rf_b.ports["i1"])

    # drive
    channels["L3-15"] = Channel(name="L3-15", port=qcm_rf0.ports["o1"])
    channels["L3-11"] = Channel(name="L3-11", port=qcm_rf1.ports["o1"])
    channels["L3-12"] = Channel(name="L3-12", port=qcm_rf1.ports["o2"])
    channels["L3-13"] = Channel(name="L3-13", port=qcm_rf2.ports["o1"])
    channels["L3-14"] = Channel(name="L3-14", port=qcm_rf2.ports["o2"])

    # flux
    channels["L4-5"] = Channel(name="L4-5", port=qcm_bb0.ports["o1"])
    channels["L4-1"] = Channel(name="L4-1", port=qcm_bb1.ports["o1"])
    channels["L4-2"] = Channel(name="L4-2", port=qcm_bb1.ports["o2"])
    channels["L4-3"] = Channel(name="L4-3", port=qcm_bb1.ports["o3"])
    channels["L4-4"] = Channel(name="L4-4", port=qcm_bb1.ports["o4"])

    # TWPA
    channels["L4-26"] = Channel(name="L4-4", port=None)

    platform = Platform(
        name="qw5q_gold_qblox",
        runcard=runcard,
        instruments=instruments,
        channels=channels,
    )

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


# Drive:
# L3-15:mod8-o1 q0
# L3-11:mod3-o1 q1
# L3-12:mod3-o2 q2
# L3-13:mod4-o1 q3
# L3-14:mod4-o2 q4


# Flux:
# L4-5:mod5-o1 q0
# L4-1:mod2-o1 q1
# L4-2:mod2-o2 q2
# L4-3:mod2-o3 q3
# L4-4:mod2-o4 q4


# Readout out:
# L3-25:mod12 and mod10 (out)
# L2-25:mod12 and mod10 (in)

# Cluster IP:
# 192.168.0.6


# # no bias line, using qblox offset from qcm_bbc
# channels: [
#   'L2-5a','L2-5b', 'L3-25a', 'L3-25b', #RO channels: Ro lines L2-5 and L3-25 splitted
#   'L3-15', 'L3-11', 'L3-12', 'L3-13', 'L3-14', 'L3-16', # Drive channels q0, q1, q2, q3, q4 | not used ports label: L3-16
#   'L4-5', 'L4-1', 'L4-2', 'L4-3', 'L4-4', 'L4-6', 'L4-7', 'L4-8', # Flux channels q0, q1, q2, q3, q4 | not used labels: 'L4-6', 'L4-7', 'L4-8'
# ]

# # [ReadOut, QubitDrive, QubitFlux, QubitBias]
# qubit_channel_map:
#     0:   [L3-25a, L3-15, L4-5, null] #q0
#     1:   [L3-25a, L3-11, L4-1, null] #q1
#     2:   [L3-25b, L3-12, L4-2, null] #q2
#     3:   [L3-25b, L3-13, L4-3, null] #q3
#     4:   [L3-25b, L3-14, L4-4, null] #q4
#     5:   [L3-25a,  null, null, null] #q5 witness
