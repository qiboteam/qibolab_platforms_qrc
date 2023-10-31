import argparse
import pathlib

from qibocal.protocols.characterization import Operation
from qibolab import create_platform

MESSAGE_FILE = "message.txt"

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


def generate_message(name, assigment_fidelities, qnds, t1s, t2s, gate_fidelity, time):
    """Generates message that is added to GitHub comments."""
    path = pathlib.Path.cwd() / MESSAGE_FILE
    with open(path, "w") as file:
        file.write(f"Run on platform `%s` completed in %.2fsec! :atom:" % (name, time))
        file.write("\n\nT1:\n")
        for qubit, t1 in t1s.items():
            file.write(f"{qubit}: {t1/1000:.2f} us\n")
        file.write("\n\nT2:\n")
        for qubit, t2 in t2s.items():
            file.write(f"{qubit}: {t2/1000:.2f} us\n")
        file.write("\n\nReadout assignment fidelities:\n")
        for qubit, fidelity in assigment_fidelities.items():
            file.write(f"{qubit}: {fidelity:.3f}\n")
        file.write("\n\nReadout QND:\n")
        for qubit, qund in qnds.items():
            file.write(f"{qubit}: {qnd:.3f}\n")
        # FIXME: several gate fidelities when RB data gets changed
        file.write("\n\nGate fidelities:\n")
        file.write(f" {gate_fidelity:.3f}\n")


def main(name):
    """Execute single shot classification routine on the given platform."""
    routines = [
        Operation.readout_characterization.value,
        Operation.t1_msr.value,
        Operation.t2_msr.value,
        Operation.standard_rb.value,
    ]

    parameters = [
        routines[0].parameters_type.load(dict(nshots=10000)),
        routines[1].parameters_type.load(
            dict(
                delay_before_readout_start=50,
                delay_before_readout_end=200000,
                delay_before_readout_step=2500,
                nshots=1024,
            )
        ),
        routines[2].parameters_type.load(
            dict(
                delay_between_pulses_start=50,
                delay_between_pulses_end=200000,
                delay_between_pulses_step=2500,
                nshots=1024,
            )
        ),
        routines[3].parameters_type.load(
            dict(
                depths=[10, 100, 150, 200, 250, 300],
                niter=8,
                nshots=256,
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
    for routine, d in zip(routines, data):
        fit, time = routine.fit(d)
        fits.append(fit)
        fit_time += time

    generate_message(
        name,
        fits[0].fidelity,
        fits[0].qnd,
        fits[1].t1,
        fits[2].t2,
        fits[3].pulse_fidelity,
        acquisition_time + fit_time,
    )


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
