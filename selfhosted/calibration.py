import json
import pathlib

import click
import yaml
from qibocal.cli.acquisition import acquire as acquisition
from qibocal.cli.fit import fit
from qibolab import create_platform

RUNCARD = pathlib.Path(__file__).parent / "actions.yml"
FOLDER = "single_shot"


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

    with open(pathlib.Path.cwd() / "fidelities.txt", "w") as file:
        for qubit, fidelity in results['"assignment_fidelity"'].items():
            file.write(f"{qubit}: {fidelity}\n")


if __name__ == "__main__":
    main()
