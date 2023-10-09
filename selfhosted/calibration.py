import json
import pathlib

import click
import yaml
from qibocal.cli.acquisition import acquire as acquisition
from qibocal.cli.fit import fit
from qibolab import create_platform

RUNCARD = pathlib.Path(__file__).parent / "actions.yml"
FOLDER = "single_shot"
MESSAGE_FILE = "message.txt"


def generate_message(name, fidelities):
    """Generates message that is added to GitHub comments."""
    path = pathlib.Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(f"Run on platform `{name}` completed! :atom:\n\n")
        file.write("Readout assignment fidelities:\n")
        for qubit, fidelity in fidelities.items():
            file.write(f"{qubit}: {fidelity}\n")


@click.command()
@click.argument("name", type=str)
def main(name):
    card = yaml.safe_load(RUNCARD.read_text())

    platform = create_platform(name)
    card["platform"] = name
    card["qubits"] = qubits = list(platform.qubits)

    acquisition(card, FOLDER, force=True)
    folder_path = pathlib.Path.cwd() / FOLDER
    fit(folder_path, update=True)

    results_path = folder_path / "data" / "single shot_0" / "results.json"
    with open(results_path) as file:
        results = json.load(file)

    generate_message(name, results['"assignment_fidelity"'])


if __name__ == "__main__":
    main()
