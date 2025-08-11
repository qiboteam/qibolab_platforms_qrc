import warnings
from dataclasses import asdict

from qibolab import create_platform


def _calibrate_readout_mixer(platform, controller, config, qubit_names):
    lo_frequency = None
    if_frequencies = []
    for q in qubit_names:
        qubit = platform.qubits[q]
        # element = f"readout{qubit.name}"
        if lo_frequency is None:
            lo_frequency = platform.config(platform.channels[qubit.probe].lo).frequency
        else:
            assert (
                lo_frequency
                == platform.config(platform.channels[qubit.probe].lo).frequency
            ), "Qubits on same probe line must have the same LO frequency."
        rf_freq = platform.config(qubit.probe).frequency
        if_frequencies.append(rf_freq - lo_frequency)

    qmachine = controller.manager.open_qm(config)
    qmachine.calibrate_element(qubit.acquisition, {lo_frequency: tuple(if_frequencies)})
    qmachine.close()


def _calibrate_drive_mixers(platform, controller, config, qubit_names):
    for q in qubit_names:
        qubit = platform.qubits[q]
        lo_frequency = platform.config(platform.channels[qubit.drive].lo).frequency
        rf_freq = platform.config(qubit.drive).frequency
        if_frequency = rf_freq - lo_frequency

        qmachine = controller.manager.open_qm(config)
        qmachine.calibrate_element(
            qubit.drive, {lo_frequency: (if_frequency, -if_frequency)}
        )
        qmachine.close()


def _controllers_config(platform):
    """Create a QM config that only contains controllers and elements (no pulses)."""
    _channel_types = ["acquisition", "drive"]
    channels = []
    for qubit in platform.qubits.values():
        channels.extend(
            getattr(qubit, n) for n in _channel_types if getattr(qubit, n) is not None
        )

    controller = platform._controller
    controller.configure_channels(platform.parameters.configs, channels)
    return asdict(controller.config)


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
    import os
    platform_name = os.environ.get("QIBO_PLATFORM", "qpu118")
    platform = create_platform(platform_name)
    controller = platform.instruments["qm"]
    controller.write_calibration = True
    controller.connect()

    config = _controllers_config(platform)

    _run_until_success(
        _calibrate_readout_mixer,
        platform,
        controller,
        config,
        [0, 1, 2],
        label="readout",
    )
    _run_until_success(
        _calibrate_drive_mixers,
        platform,
        controller,
        config,
        [0, 1, 2],
        label="drive",
    )

    controller.disconnect()
