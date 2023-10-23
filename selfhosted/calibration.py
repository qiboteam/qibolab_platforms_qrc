import argparse
import pathlib

from qibocal.protocols.characterization import Operation
from qibolab import create_platform

MESSAGE_FILE = "message.txt"

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


def generate_message(name, fidelities, time):
    """Generates message that is added to GitHub comments."""
    path = pathlib.Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(f"Run on platform `%s` completed in %.2fsec! :atom:" % (name, time))
        file.write("\n\nReadout assignment fidelities:\n")
        for qubit, fidelity in fidelities.items():
            file.write(f"{qubit}: {fidelity}\n")


def main(name):
    """Execute single shot classification routine on the given platform."""
    routine = Operation.single_shot_classification.value
    params = routine.parameters_type.load(dict(nshots=5000))

    platform = create_platform(name)
    qubits = platform.qubits

    data, acquisition_time = routine.acquisition(
        params=params, platform=platform, qubits=qubits
    )
    fit, fit_time = routine.fit(data)

    generate_message(name, fit.assignment_fidelity, acquisition_time + fit_time)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
