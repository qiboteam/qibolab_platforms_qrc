import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster_qcm_bb import QcmBb
from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

ADDRESS = "192.168.0.2"
FOLDER = pathlib.Path(__file__).parent


def create():
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:15"),  # readout  o=L3-31r, i=L2-1
        "qcm_rf0": QrmRf("qcm_rf0", f"{ADDRESS}:13"),  # drive L-3-31d
    }

    controller = QbloxController("qblox_controller", ADDRESS, modules)
    # twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    instruments = {
        controller.name: controller,
        #     twpa_pump0.name: twpa_pump0,
    }
    instruments.update(modules)
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-31r", port=modules["qrm_rf0"].ports("o1"))
    # Feedback
    channels |= Channel(name="L2-1", port=modules["qrm_rf0"].ports("i1", out=False))
    # Drive
    channels |= Channel(name="L3-31d", port=modules["qcm_rf0"].ports("o1"))

    channels |= Channel(name="L99", port=modules["qcm_rf0"].ports("i1", out=False))

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )
