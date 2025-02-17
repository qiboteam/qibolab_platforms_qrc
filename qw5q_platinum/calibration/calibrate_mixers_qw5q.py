
import warnings

from qibolab import create_platform
from qibolab.instruments.qm.controller import controllers_config


def _calibrate_readout_mixer(platform, controller, config, qubit_names):
    lo_frequency = None
    if_frequencies = []
    for q in qubit_names:
        qubit = platform.qubits[q]
        element = f"readout{qubit.name}"
        if lo_frequency is None:
            lo_frequency = qubit.readout.lo_frequency
        else:
            assert (
                lo_frequency == qubit.readout.lo_frequency
            ), "Qubits on same probe line must have the same LO frequency."
        if_frequencies.append(qubit.native_gates.MZ.frequency - lo_frequency)

    qmachine = controller.manager.open_qm(config.__dict__)
    qmachine.calibrate_element(element, {lo_frequency: tuple(if_frequencies)})
    qmachine.close()

def _calibrate_drive_mixers(platform, controller, config, qubit_names):
    for q in qubit_names:
        qubit = platform.qubits[q]
        element = f"drive{qubit.name}"
        lo_frequency = qubit.drive.lo_frequency
        if_frequency = qubit.native_gates.RX.frequency - lo_frequency

        qmachine = controller.manager.open_qm(config.__dict__)
        qmachine.calibrate_element(element, {lo_frequency: (if_frequency,)})
        qmachine.close()


def _run_until_success(fn, *args, label):
    while True:
        try:
            fn(*args)
            print(f"Mixer calibration for {label} finished successfully")
            break
        except RuntimeWarning as w:
            print(
                f"Issue encountered while running mixer calibration for {label} mixer. Retrying..."
            )


if __name__ == "__main__":
    warnings.filterwarnings("error", category=RuntimeWarning, message="invalid value")

    platform = create_platform("qw5q_platinum")
    controller = platform.instruments["qm"]
    controller.write_calibration = True
    controller.connect()

    config = controllers_config(
        list(platform.qubits.values()), controller.time_of_flight, controller.smearing
    )
    _run_until_success(
        _calibrate_readout_mixer,
        platform,
        controller,
        config,
        [0,1,2,3,4],
        label="readout",
    )
    _run_until_success(
        _calibrate_drive_mixers,
        platform,
        controller,
        config,
        [0,1,2,3,4],
        label="drive",
    )

    controller.disconnect()
