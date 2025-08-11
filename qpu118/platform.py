import pathlib
from time import gmtime, strftime

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
    """TII 3q-chip fixed frequency controlled with Quantum Machines OPX1000 and Octaves."""
    # qubits = {i: Qubit.default(i,drive_extra={(2-i): f"{i}/drive_extra"}) for i in range(3) } # Added by Luca and commented next 5 rows
    # qubits = {i: Qubit.default(i) for i in range(3)}
    qubits = {}
    qubits[0] = Qubit.default(0, drive_extra={(1, 2): "0/drive12", 1: "01/drive"})
    qubits[1] = Qubit.default(1, drive_extra={(1, 2): "1/drive12", 0: "10/drive"})
    qubits[2] = Qubit.default(2)
    # Create channels and connect to instrument ports
    # Readout
    channels = {}
    for q in qubits.values():
        channels[q.probe] = IqChannel(
            device="octave1", path="1", mixer=None, lo="probe_lo"
        )
    # Acquire
    for q in qubits.values():
        channels[q.acquisition] = AcquisitionChannel(
            device="octave1", path="1", twpa_pump=None, probe=q.probe
        )
    # Drive
    channels[qubits[0].drive] = IqChannel(
        device="octave2", path="1", mixer=None, lo="0/drive_lo" #L3-27
    )
    channels[qubits[1].drive] = IqChannel(
        device="octave2", path="4", mixer=None, lo="1/drive_lo" #L3-26
    )
    channels[qubits[2].drive] = IqChannel(
        device="octave2", path="3", mixer=None, lo="2/drive_lo" #L3-25
    )
    # commented this and also commented 01 and 10 drive channels in the parameters

    channels[qubits[0].drive_extra[1]] = IqChannel(
        device="octave2", path="1", mixer=None, lo="0/drive_lo"
    )
    channels[qubits[1].drive_extra[0]] = IqChannel(
        device="octave2", path="4", mixer=None, lo="1/drive_lo"
    )

    octaves = {
        "octave1": Octave("octave1", port=11248, connectivity="con1/1"),
        "octave2": Octave("octave2", port=11245, connectivity="con1/2"),
    }
    fems = {"con1/1": "LF", "con1/2": "LF"}
    controller = QmController(
        address="192.168.0.102:80",
        octaves=octaves,
        fems=fems,
        channels=channels,
        cluster_name="Cluster_2",
        calibration_path=FOLDER,
        #    script_file_name=f"Z_qua_scripts/qua_script_{strftime('%d_%b_%H_%M_%S', gmtime())}.py",
    )
    instruments = {"qm": controller}
    return Platform.load(path=FOLDER, instruments=instruments, qubits=qubits)
