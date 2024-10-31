import pathlib
from qibolab import create_platform

FOLDER = pathlib.Path(__file__).parent
QUBITS = {"D1", "D3"}


def create():
    platform = create_platform("qw11q")
    platform.name = FOLDER.name
    platform.qubits = {q: v for q, v in platform.qubits.items() if q in QUBITS}
    for q in list(platform.parameters.native_gates.single_qubit):
        if q not in QUBITS:
            del platform.parameters.native_gates.single_qubit[q]
    for q1, q2 in list(platform.parameters.native_gates.two_qubit):
        if q1 not in QUBITS or q2 not in QUBITS:
            del platform.parameters.native_gates.two_qubit[(q1, q2)]

    return platform
