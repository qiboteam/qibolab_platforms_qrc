import argparse
import pathlib

from qibocal.protocols.characterization import Operation
from qibolab import create_platform

MESSAGE_FILE = "message.txt"

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


def generate_message(name, assigment_fidelities, t1s, t2s, gate_fidelities, time):
    """Generates message that is added to GitHub comments."""
    path = pathlib.Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(f"Run on platform `%s` completed in %.2fsec! :atom:" % (name, time))
        file.write("\n\nReadout assignment fidelities:\n")
        for qubit, fidelity in assigment_fidelities.items():
            file.write(f"{qubit}: {fidelity}\n")
        file.write("\n\nT1:\n")
        for qubit, t1 in t1s.items():
            file.write(f"{qubit}: {t1}\n")
        file.write("\n\nT2:\n")
        for qubit, t2 in t2s.items():
            file.write(f"{qubit}: {t2}\n")
        file.write("\n\nGate fidelities:\n")
        for qubit, gate_fidelity in gate_fidelities.items():
            file.write(f"{qubit}: {gate_fidelity}\n")


def main(name):
    """Execute single shot classification routine on the given platform."""
    routines = [
        Operation.single_shot_classification.value,
        Operation.t1.value,
        Operation.t2.value,
        Operation.standard_rb.value,
    ]

    parameters = [
        routines[0].parameters_type.load(dict(nshots=5000)),
        routines[1].parameters_type.load(dict()),
        routines[2].parameters_type.load(dict()),
        routines[3].parameters_type.load(
            dict(
                depths=[10, 50, 100, 150, 200, 250, 300],
                niter=10,
                nshots=128,
            )
        ),
    ]

    data = []
    acquisition_time = 0

    platform = create_platform(name)
    qubits = platform.qubits

    platform.connect()
    platform.setup()
    platform.start()

    for routine, params in zip(routines, parameters):
        d, time = routine.acquisition(params=params, platform=platform, qubits=qubits)
        data.append(d)
        acquisition_time += time

    platform.stop()
    platform.disconnect()

    fits = []
    fit_time = 0
    for routine in routines:
        fit, time = routine.fit(data)
        fits.append(fit)
        fit_time += time

    generate_message(
        name,
        fits[0].assignment_fidelity,
        fits[1].t1,
        fits[2].t2,
        fits[3].pulse_fidelity,
        acquisition_time + fit_time,
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
