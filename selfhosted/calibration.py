import argparse
import getpass
import io
import json
import logging
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from qibo.config import log
from qibocal.auto.runcard import Runcard
from qibocal.cli.acquisition import acquire
from qibocal.cli.fit import fit
from qibocal.cli.report import report
from qibocal.cli.upload import upload_report
from qibolab import create_platform

MESSAGE_FILE = "message.txt"

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


def get_report_url(output):
    return output.split("\n")[-2]


@dataclass
class Experiment:
    routine: str
    params: dict
    header: str
    attribute: str
    formatter: Callable = field(default=lambda x: f"{x:.3f}")
    acquisition_time: float = 0
    fit_time: float = 0

    @property
    def data_path(self):
        """Path to qibocal output folder."""
        return Path.cwd() / self.routine

    @property
    def report_path(self):
        return self.data_path / "index.html"

    @property
    def fit_path(self):
        """Path to file containing fit results."""
        return self.data_path / "data" / f"{self.routine}_0" / "results.json"

    @property
    def total_time(self):
        return self.acquisition_time + self.fit_time

    def __call__(self, platform, qubits):
        action = {
            "id": self.routine,
            "operation": self.routine,
            "priority": 0,
            "parameters": self.params,
        }
        runcard = Runcard.load(
            {
                "platform": platform,
                "qubits": qubits,
                "actions": [action],
            }
        )
        try:
            start_time = time.time()
            acquire(runcard, self.routine, force=True)
            self.acquisition_time = time.time() - start_time
            start_time = time.time()
            fit(Path.cwd() / self.routine, update=False)
            self.fit_time = time.time() - start_time
            report(self.data_path)
        except:
            logging.error(traceback.format_exc())

    def report(self, file):
        file.write(f"\n{self.header}: ")
        if self.report_path.exists():
            output = io.StringIO()
            log.addHandler(logging.StreamHandler(output))
            upload_report(self.data_path, tag="CI", author=getpass.getuser())
            file.write(get_report_url(output.getvalue()))
            file.write("\n")
            data = json.loads(self.fit_path.read_text())
            for qubit, value in data[f'"{self.attribute}"'].items():
                file.write(f"{qubit}: {self.formatter(value)}\n")
        else:
            file.write("execution failed :worried:")


def convert_to_us(x):
    return f"{x / 1000:.2f} us"


def main(name):
    """Execute single shot classification routine on the given platform."""
    platform = create_platform(name)
    qubits = platform.qubits

    max_time = max(int(5 * max(qubit.T1 for qubit in qubits.values())), 20000)
    step = max_time // 25
    experiments = [
        Experiment(
            "readout_characterization",
            dict(nshots=10000),
            header="Readout assignment fidelities",
            attribute="assignment_fidelity",
        ),
        Experiment(
            "t1_signal",
            dict(
                delay_before_readout_start=50,
                delay_before_readout_end=max_time,
                delay_before_readout_step=step,
                nshots=2000,
            ),
            header="T1",
            attribute="t1",
            formatter=convert_to_us,
        ),
        Experiment(
            "t2_signal",
            dict(
                delay_between_pulses_start=50,
                delay_between_pulses_end=max_time,
                delay_between_pulses_step=step,
                nshots=2000,
            ),
            header="T2",
            attribute="t2",
            formatter=convert_to_us,
        )
        # Experiment(
        #     Operation.standard_rb.value,
        #     dict(
        #         depths=[10, 100, 150, 200, 250, 300],
        #         niter=8,
        #         nshots=256,
        #     )
        #     "Gate fidelities",
        # )
    ]

    platform.connect()
    platform.setup()
    platform.start()

    for experiment in experiments:
        experiment(platform.name, list(qubits))

    platform.stop()
    platform.disconnect()

    total_time = sum(experiment.total_time for experiment in experiments)
    path = Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(
            f"Run on platform `%s` completed in %.2fsec! :atom:\n" % (name, total_time)
        )
        for experiment in experiments:
            experiment.report(file)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
