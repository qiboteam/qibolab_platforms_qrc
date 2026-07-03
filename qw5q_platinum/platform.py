import pathlib

from qibolab import (
    AcquisitionChannel,
    ConfigKinds,
    DcChannel,
    Hardware,
    IqChannel,
    Qubit,
)
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


def create():
    """QuantWare 5q-chip controlled with Quantum Machines OPX1000 and Octaves."""
    # qubits = {i: Qubit.default(i,drive_extra={(1, 2): f"{i}/drive12"}) for i in range(5)}
    qubits = {i: Qubit.default(i) for i in range(5)}

    # Create channels and connect to instrument ports
    # Readout
    channels = {}
    for q in qubits.values():
        channels[q.probe] = IqChannel(
            device="oct2", path="1", mixer=None, lo="probe_lo"
        )
    # Acquire
    for q in qubits.values():
        channels[q.acquisition] = AcquisitionChannel(
            device="oct2", path="1", twpa_pump="twpa", probe=q.probe
        )
    # Drive
    channels[qubits[0].drive] = IqChannel(
        device="oct2", path="2", mixer=None, lo="01/drive_lo"
    )
    channels[qubits[1].drive] = IqChannel(
        device="oct2", path="3", mixer=None, lo="01/drive_lo"
    )
    channels[qubits[2].drive] = IqChannel(
        device="oct3", path="2", mixer=None, lo="2/drive_lo"
    )
    channels[qubits[3].drive] = IqChannel(
        device="oct2", path="4", mixer=None, lo="3/drive_lo"
    )
    channels[qubits[4].drive] = IqChannel(
        device="oct3", path="4", mixer=None, lo="4/drive_lo"
    )
    # Flux
    channels[qubits[0].flux] = DcChannel(device="con1/4", path="1")
    channels[qubits[1].flux] = DcChannel(device="con1/4", path="2")
    channels[qubits[2].flux] = DcChannel(device="con1/4", path="3")
    channels[qubits[3].flux] = DcChannel(device="con1/4", path="4")
    channels[qubits[4].flux] = DcChannel(device="con1/4", path="5")

    octaves = {
        "oct2": Octave("oct2", port=00000, connectivity="con1/2"),
        "oct3": Octave("oct3", port=00000, connectivity="con1/3"),
    }
    fems = {"con1/2": "LF", "con1/3": "LF", "con1/4": "LF"}
    controller = QmController(
        address="192.168.0.102:80",
        octaves=octaves,
        fems=fems,
        channels=channels,
        cluster_name="Cluster_1",
        calibration_path=FOLDER,
        # script_file_name="qua_script.py",
    )
    instruments = {
        "qm": controller,
        "twpa": SGS100A(address="192.168.0.38", turn_off_on_disconnect=False),
    }
    return Hardware(instruments=instruments, qubits=qubits)
