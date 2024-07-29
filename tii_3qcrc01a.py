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
 
NAME = "tii_3qcrc01a"
ADDRESS = "192.168.0.20"
RUNCARD = pathlib.Path(__file__).parent / "tii_3qcrc01a.yml"
 
 
def create(runcard_path=RUNCARD):
    """3qubit chip with qblox .20.
 
    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(runcard_path)
    cluster = Cluster(
        name="cluster",
        address=ADDRESS,
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.EXTERNAL),
    )
    modules = {
        "qcm_rf0": ClusterQCM_RF(
            "qcm_rf0", f"{ADDRESS}:20", cluster
        ),  # qubits q1, q2
        "qrm_rf0": ClusterQRM_RF(
            "qrm_rf0", f"{ADDRESS}:4", cluster
        ),   
    }
    controller = QbloxController("qblox_controller", cluster, modules)
    #twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    #twpa_pump1 = SGS100A(name="twpa_pump1", address="192.168.0.39")
 
    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)
 
    # #########################################################################################################
 
    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="V2", port=modules["qrm_rf0"].ports["o1"])
    # Feedback
    channels |= Channel(name="W5", port=modules["qrm_rf0"].ports["i1"])
     # Drive
    channels |= Channel(name="V6", port=modules["qcm_rf0"].ports["o1"])
    channels |= Channel(name="V7", port=modules["qcm_rf0"].ports["o2"])
 
    channels |= Channel(name="dummy", port=None)
 
    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)
 
    # assign channels to qubits    
    for q in range(0, 2):  # q0, q1
        qubits[q].readout = channels["V2"]
        qubits[q].feedback = channels["W5"]
    
    qubits[0].drive = channels[f"V6"]
    qubits[1].drive = channels[f"V7"]

    channels[f"V6"].qubit = qubits[0]
    channels[f"V7"].qubit = qubits[1]

 
    settings = load_settings(runcard)
 
    return Platform(
        "tii_3qcrc01a", qubits, pairs, instruments, settings, resonator_type="2D"
    )