import argparse
import logging
import pathlib
import traceback
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from qibocal.auto.operation import Routine
from qibocal.protocols.characterization import Operation
from qibolab import create_platform

MESSAGE_FILE = "message.txt"

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


@dataclass
class Experiment:
    routine: Routine
    params: dict
    header: str
    attribute: str
    formatter: Callable = field(default=lambda x: f"{x:.3f}")
    fit: Optional["test"] = None
    acquisition_time: float = 0
    fit_time: float = 0

    @property
    def total_time(self):
        return self.acquisition_time + self.fit_time

    def __call__(self, platform, qubits):
        params = self.routine.parameters_type.load(self.params)
        try:
            data, self.acquisition_time = self.routine.acquisition(
                params=params, platform=platform, qubits=qubits
            )
            self.fit, self.fit_time = self.routine.fit(data)
        except:
            logging.error(traceback.format_exc())

    def report(self, file):
        file.write(f"\n{self.header}:")
        if self.fit is None:
            file.write(" execution failed :worried:\n")
        else:
            file.write("\n")
            for qubit, value in getattr(self.fit, self.attribute).items():
                file.write(f"{qubit}: {self.formatter(value)}\n")


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
            Operation.readout_characterization.value,
            dict(nshots=10000),
            header="Readout assignment fidelities",
            attribute="assignment_fidelity",
        ),
        Experiment(
            Operation.t1_signal.value,
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
            Operation.t2_signal.value,
            dict(
                delay_between_pulses_start=50,
                delay_between_pulses_end=max_time,
                delay_between_pulses_step=step,
                nshots=2000,
            ),
            header="T2",
            attribute="t2",
            formatter=convert_to_us,
        ),
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
        experiment(platform, qubits)

    platform.stop()
    platform.disconnect()

    total_time = sum(experiment.total_time for experiment in experiments)
    path = pathlib.Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(
            f"Run on platform `%s` completed in %.2fsec! :atom:\n" % (name, total_time)
        )
        for experiment in experiments:
            experiment.report(file)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
