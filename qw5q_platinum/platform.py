import pathlib

from qibolab import (
    AcquisitionChannel,
    Channel,
    ConfigKinds,
    DcChannel,
    IqChannel,
    Platform,
    Qubit,
)
from qibolab.instruments.qm import Octave, QmConfigs, QmController
from qibolab.instruments.rohde_schwarz import SGS100A

FOLDER = pathlib.Path(__file__).parent

# Register QM-specific configurations for parameters loading
ConfigKinds.extend([QmConfigs])


def create():
    """Line D of QuantWare 21q-chip controlled with Quantum Machines.

    Qubits D1, D2, D3 have been tested to work.
    """
    qubits = {i: Qubit.default(i) for i in range(5)}

    # Create channels and connect to instrument ports
    # Readout
    channels = {}
    for q in qubits.values():
        channels[q.probe] = IqChannel(
            device="octave2", path="1", mixer=None, lo="probe_lo"
        )
    # Acquire
    for q in qubits.values():
        channels[q.acquisition] = AcquisitionChannel(
            device="octave2", path="1", twpa_pump="twpa", probe=q.probe
        )
    # Drive
    channels[qubits[0].drive] = IqChannel(
        device="octave1", path="2", mixer=None, lo="01/drive_lo"
    )
    channels[qubits[1].drive] = IqChannel(
        device="octave1", path="3", mixer=None, lo="01/drive_lo"
    )
    channels[qubits[2].drive] = IqChannel(
        device="octave1", path="1", mixer=None, lo="2/drive_lo"
    )
    channels[qubits[3].drive] = IqChannel(
        device="octave1", path="4", mixer=None, lo="3/drive_lo"
    )
    channels[qubits[4].drive] = IqChannel(
        device="octave2", path="2", mixer=None, lo="4/drive_lo"
    )
    # Flux
    channels[qubits[0].flux] = DcChannel(device="con1/4", path="4")
    channels[qubits[1].flux] = DcChannel(device="con1/4", path="1")
    channels[qubits[2].flux] = DcChannel(device="con1/4", path="3")
    channels[qubits[3].flux] = DcChannel(device="con1/4", path="2")
    channels[qubits[4].flux] = DcChannel(device="con1/4", path="5")

    octaves = {
        "octave1": Octave("octave1", port=11250, connectivity="con1/1"),
        "octave2": Octave("octave2", port=11251, connectivity="con1/2"),
    }
    fems = {"con1/1": "LF", "con1/2": "LF", "con1/4": "LF"}
    controller = QmController(
        address="192.168.0.102:80",
        octaves=octaves,
        fems=fems,
        channels=channels,
        # calibration_path=FOLDER,
        script_file_name="qua_script.py",
    )
    instruments = {"qm": controller, "twpa": SGS100A(address="192.168.0.38")}
    return Platform.load(path=FOLDER, instruments=instruments, qubits=qubits)
