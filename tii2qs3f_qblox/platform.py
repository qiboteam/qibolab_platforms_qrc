import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster_qcm_bb import QcmBb
from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

ADDRESS = "192.168.0.3"
FOLDER = pathlib.Path(__file__).parent


def create():
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qcm_bb0": QcmBb("qcm_bb0", f"{ADDRESS}:2"),
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:6"),
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:16"),
    }

    # DEBUG: debug folder = report folder
    import os
    from datetime import datetime

    QPU = "tii2qs3f"
    debug_folder = f"/home/users/alvaro.orgaz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    if not os.path.exists(debug_folder):
        os.makedirs(debug_folder)
    for name in modules:
        modules[name]._debug_folder = debug_folder

    controller = QbloxController("qblox_controller", ADDRESS, modules)

    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    channels = ChannelMap()
    # Readout Probe
    channels |= Channel(name="L3-26", port=modules["qrm_rf0"].ports("o1"))
    # Readout Feedback
    channels |= Channel(name="L2-02", port=modules["qrm_rf0"].ports("i1", out=False))
    # Drive
    channels |= Channel(name="L3-03", port=modules["qcm_rf0"].ports("o1"))
    channels |= Channel(name="L3-04", port=modules["qcm_rf0"].ports("o2"))
    # Flux
    channels |= Channel(name="L1-05", port=modules["qcm_bb0"].ports("o1"))
    channels |= Channel(name="dummy", port=modules["qcm_bb0"].ports("o2"))

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[1].readout = channels["L3-26"]
    qubits[1].feedback = channels["L2-02"]
    qubits[1].drive = channels["L3-03"]
    qubits[1].flux = channels["L1-05"]
    channels["L1-05"].qubit = qubits[1]
    qubits[1].flux.max_bias = 2.5

    qubits[2].readout = channels["L3-26"]
    qubits[2].feedback = channels["L2-02"]
    qubits[2].drive = channels["L3-04"]

    qubits[2].flux = channels["dummy"]
    channels["dummy"].qubit = qubits[2]
    qubits[2].flux.max_bias = 2.5

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )
