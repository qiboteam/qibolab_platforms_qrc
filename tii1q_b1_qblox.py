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

#from qibolab.instruments.rfsoc import RFSoC


NAME = "tii1q_b1_qblox"
ADDRESS = "192.168.0.6"
TIME_OF_FLIGHT = 500
#
RUNCARD = pathlib.Path(__file__).parent / "tii1q_b1.yml"

TWPA_ADDRESS = "192.168.0.31"

instruments_settings = {
    "cluster": Cluster_Settings(reference_clock_source=ReferenceClockSource.INTERNAL),
    "qrm_rf_a": ClusterQRM_RF_Settings(  # q0,q1,q5, 1-2-4?
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-22_a",
                attenuation=30,  # 38
                lo_frequency=7_250_000_000,
                gain=1,
            ),
            "i1": QbloxInputPort_Settings(
                channel="L1-2",
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=900,
            ),
        }
    ),
    "qcm_rf0": ClusterQCM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel="L3-22_b",
                attenuation=8,
                lo_frequency=5_300_000_000,
                gain=1,
            ),
            "o2": ClusterRF_OutputPort_Settings( # Not used
                channel="L3-13",
                attenuation=20,
                lo_frequency=6_961_018_001,
                gain=1,
            ),
        }
    ),
}
def create(runcard_path=RUNCARD):
    """Platform for Qblox.

    IPs and other instrument related parameters are hardcoded in.
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
    qrm_rf_a = instantiate_module(
        modules, ClusterQRM_RF, "qrm_rf_a", "192.168.0.6:20", instruments_settings
    )
    qcm_rf0 = instantiate_module(
        modules, ClusterQCM_RF, "qcm_rf0", "192.168.0.6:16", instruments_settings
    )  

    controller = QbloxController("qblox_controller", cluster, modules)

    # Create channel objects
    channels = {}
    # readout
    channels["L3-22_a"] = Channel(name="L3-22_a", port=qrm_rf_a.ports["o1"])
    # feedback
    channels["L1-2"] = Channel(name="L1-2", port=qrm_rf_a.ports["i1"])
    # drive
    channels["L3-22_b"] = Channel(name="L3-22_b", port=qcm_rf0.ports["o1"])




    # TWPA

    twpa_lo = SGS100A("twpa_lo", TWPA_ADDRESS)
    twpa_lo.frequency = 6_433_500_000
    twpa_lo.power = 2.5
    channels["L3-24"] = Channel(name="L3-24", port=None) 
    channels["L3-24"].local_oscillator = twpa_lo

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)
    # assign channels to qubits
    qubits[0].readout = channels["L3-22_a"]
    qubits[0].feedback = channels["L1-2"]
    qubits[0].drive = channels["L3-22_b"]
    qubits[0].twpa = channels["L3-24"]

    instruments = {
        controller.name: controller,
        twpa_lo.name: twpa_lo,
    }

    settings = load_settings(runcard)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="3D")
