import pathlib

import networkx as nx
import yaml
from qibolab.channels import Channel, ChannelMap

# from qibolab.instruments.erasynth import ERA
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

NAME = "qblox_tii2q2"
ADDRESS = "192.168.0.2"
TIME_OF_FLIGHT = 500
RUNCARD = pathlib.Path(__file__).parent / "tii2q2.yml"
TWPA_ADDRESS = "192.168.0.34"

instruments_settings = {
    "cluster": Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    "qrm_rf_a": ClusterQRM_RF_Settings(  # q0,q1,q5
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-26",
                attenuation=56,  # 38
                lo_frequency=7_250_000_000,
                gain=1,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L2-02",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=900,
            ),
        }
    ),
    "qrm_rf_b": ClusterQRM_RF_Settings(  # q2,q3,q4
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-03",
                attenuation=0,
                lo_frequency=4_500_000_000,
                gain=1,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L99",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=900,
            ),
        }
    ),
    "qrm_rf_c": ClusterQRM_RF_Settings(  # q2,q3,q4
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-04",
                attenuation=3,
                lo_frequency=4_500_000_000,
                gain=1,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L99",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=900,
            ),
        }
    ),
    "qcm_bb0": ClusterQCM_BB_Settings(
        {
            "o3": ClusterBB_OutputPort_Settings(
                channel="L1-5",
                gain=0.5,
                qubit=0,  # channel="L4-3", gain=0.5, offset=-0.8893, qubit=3
            ),
        }
    ),
}


def create(runcard_path=RUNCARD):
    """TII 2q2-chip controlled using qblox cluster.

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

    qcm_bb0 = instantiate_module(
        modules, ClusterQCM_BB, "qcm_bb0", "192.168.0.2:5", instruments_settings
    )  # qubits q0
    qrm_rf_a = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_a", "192.168.0.2:12", instruments_settings
    )  # readout qubits q0 q1
    qrm_rf_b = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_b", "192.168.0.2:14", instruments_settings
    )  # control q0
    qrm_rf_c = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_c", "192.168.0.2:15", instruments_settings
    )  # control q1

    controller = QbloxController("qblox_controller", cluster, modules)
    #    twpa_pump = SGS100A(name="twpa_pump", address=TWPA_ADDRESS)

    # Create channel objects
    channels = {}
    # readout
    channels["L3-26"] = Channel(name="L3-26", port=qrm_rf_a.ports["o1"])

    # feedback
    channels["L2-02"] = Channel(name="L2-04", port=qrm_rf_a.ports["i1"])

    # drive
    channels["L3-03"] = Channel(name="L3-03", port=qrm_rf_b.ports["o1"])
    channels["L3-04"] = Channel(name="L3-04", port=qrm_rf_c.ports["o1"])

    # flux ()
    channels["L1-05"] = Channel(name="L1-05", port=qcm_bb0.ports["o3"])
    # TWPA
    #    channels["L3-29"] = Channel(name="L3-29", port=None)
    #    channels["L3-29"].local_oscillator = twpa_pump

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[0].readout = channels["L3-26"]
    qubits[0].feedback = channels["L2-02"]
    qubits[0].flux = channels["L1-05"]
    qubits[0].drive = channels["L3-03"]

    qubits[1].readout = channels["L3-26"]
    qubits[1].feedback = channels["L2-02"]
    qubits[1].drive = channels["L3-04"]

    instruments = {controller.name: controller}  # , twpa_pump.name: twpa_pump}
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        "qblox_tii2q2", qubits, pairs, instruments, settings, resonator_type="2D"
    )
