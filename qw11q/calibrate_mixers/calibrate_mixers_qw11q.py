import warnings

from qibolab import create_platform

# from qibolab.instruments.qm.controller import controllers_config # function does not exist on 0.2 for now, hence need to copy a config instead (e.g. run an experimnet (e.g. single shot) and get the ocnfig from the qua  script)
# import qibolab.instruments.qm


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

    platform = create_platform("qw11q")
    controller = platform.instruments["qm"]
    controller.write_calibration = True
    controller.connect()

    # config = controllers_config(
    #    list(platform.qubits.values()), controller.time_of_flight, controller.smearing
    # )
    config = {
        "version": 1,
        "controllers": {
            "con4": {
                "type": "opx1",
                "analog_outputs": {
                    "1": {
                        "offset": 0.09457407054642519,
                        "filter": {},
                    },
                    "2": {
                        "offset": 0.4403507148777086,
                        "filter": {
                            "feedforward": [1.0605851073784813, -0.9529722265285006],
                            "feedback": [0.890387119150019],
                        },
                    },
                    "3": {
                        "offset": 0.11716412140532566,
                        "filter": {
                            "feedforward": [1.0891790415038731, -1.024484298837039],
                            "feedback": [0.935305257333166],
                        },
                    },
                    "4": {
                        "offset": -0.474938100060548,
                        "filter": {
                            "feedforward": [1.0891790415038731, -1.024484298837039],
                            "feedback": [0.933705257333166],
                        },
                    },
                    "5": {
                        "offset": -0.3270142937133954,
                        "filter": {},
                    },
                },
                "digital_outputs": {},
                "analog_inputs": {},
            },
            "con9": {
                "type": "opx1",
                "analog_outputs": {
                    "3": {
                        "offset": 0.0,
                        "filter": {
                            "feedforward": [1.1298143371682787, -0.9007185757251136],
                            "feedback": [0.7709042385568349],
                        },
                    },
                    "4": {
                        "offset": 0.0,
                        "filter": {
                            "feedforward": [1.0891790415038731, -1.024484298837039],
                            "feedback": [0.935305257333166],
                        },
                    },
                    "5": {
                        "offset": 0.0,
                        "filter": {
                            "feedforward": [1.1298143371682787, -0.9007185757251136],
                            "feedback": [0.7709042385568349],
                        },
                    },
                    "6": {
                        "offset": 0.0,
                        "filter": {},
                    },
                    "7": {
                        "offset": 0.0,
                        "filter": {},
                    },
                },
                "digital_outputs": {},
                "analog_inputs": {},
            },
            "con2": {
                "type": "opx1",
                "analog_outputs": {
                    "1": {
                        "offset": 0,
                    },
                    "2": {
                        "offset": 0,
                    },
                    "3": {
                        "offset": 0,
                    },
                    "4": {
                        "offset": 0,
                    },
                    "7": {
                        "offset": 0,
                    },
                    "8": {
                        "offset": 0,
                    },
                },
                "digital_outputs": {
                    "1": {},
                    "3": {},
                    "7": {},
                },
                "analog_inputs": {
                    "1": {
                        "offset": 0.0,
                        "gain_db": 10,
                    },
                    "2": {
                        "offset": 0.0,
                        "gain_db": 10,
                    },
                },
            },
            "con3": {
                "type": "opx1",
                "analog_outputs": {
                    "1": {
                        "offset": 0,
                    },
                    "2": {
                        "offset": 0,
                    },
                    "5": {
                        "offset": 0,
                    },
                    "6": {
                        "offset": 0,
                    },
                    "7": {
                        "offset": 0,
                    },
                    "8": {
                        "offset": 0,
                    },
                },
                "digital_outputs": {
                    "1": {},
                    "5": {},
                    "7": {},
                },
                "analog_inputs": {
                    "1": {
                        "offset": 0,
                    },
                    "2": {
                        "offset": 0,
                    },
                },
            },
        },
        "octaves": {
            "octave2": {
                "connectivity": "con2",
                "RF_outputs": {
                    "1": {
                        "LO_frequency": 7400000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                    "2": {
                        "LO_frequency": 4900000000.0,
                        "gain": 0.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                    "4": {
                        "LO_frequency": 5900000000.0,
                        "gain": 0.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                },
                "RF_inputs": {
                    "1": {
                        "LO_frequency": 7400000000.0,
                        "LO_source": "internal",
                        "IF_mode_I": "direct",
                        "IF_mode_Q": "direct",
                    },
                },
            },
            "octave3": {
                "connectivity": "con3",
                "RF_outputs": {
                    "1": {
                        "LO_frequency": 5800000000.0,
                        "gain": 0.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                    "3": {
                        "LO_frequency": 5900000000.0,
                        "gain": 0.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                    "4": {
                        "LO_frequency": 6700000000.0,
                        "gain": 0.0,
                        "LO_source": "internal",
                        "output_mode": "triggered",
                    },
                },
                "RF_inputs": {},
            },
        },
        "elements": {
            "B1/flux": {
                "singleInput": {
                    "port": ("con4", 1),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "D1/flux": {
                "singleInput": {
                    "port": ("con9", 3),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "B2/flux": {
                "singleInput": {
                    "port": ("con4", 2),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "D2/flux": {
                "singleInput": {
                    "port": ("con9", 4),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "B3/flux": {
                "singleInput": {
                    "port": ("con4", 3),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "D3/flux": {
                "singleInput": {
                    "port": ("con9", 5),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "B4/flux": {
                "singleInput": {
                    "port": ("con4", 4),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "D4/flux": {
                "singleInput": {
                    "port": ("con9", 6),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "B5/flux": {
                "singleInput": {
                    "port": ("con4", 5),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "D5/flux": {
                "singleInput": {
                    "port": ("con9", 7),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "B1/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -277118342.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "5243483685427185520": "5243483685427185520_B1/acquisition",
                },
            },
            "B5/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 237240306.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-1121073335717786507": "-1121073335717786507_B5/acquisition",
                },
            },
            "B2/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -30845617.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-1121073335717786507": "-1121073335717786507_B2/acquisition",
                },
            },
            "B3/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 72183730.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "5983976435576360180": "5983976435576360180_B3/acquisition",
                },
            },
            "B4/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 295533056.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "7972844559298627969": "7972844559298627969_B4/acquisition",
                },
            },
            "B3/drive": {
                "RF_inputs": {
                    "port": ("octave3", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con3", 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -114627771.0,
                "operations": {
                    "-5844443819135643270": "-5844443819135643270",
                },
            },
            "B5/drive": {
                "RF_inputs": {
                    "port": ("octave3", 3),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con3", 5),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -158156525.0,
                "operations": {
                    "7080144445739131682": "7080144445739131682",
                },
            },
            "B1/drive": {
                "RF_inputs": {
                    "port": ("octave2", 2),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 3),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 100234423.0,
                "operations": {
                    "7712590452798127843": "7712590452798127843",
                },
            },
            "B4/drive": {
                "RF_inputs": {
                    "port": ("octave3", 4),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con3", 7),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 111858907.0,
                "operations": {
                    "-7160365892553629488": "-7160365892553629488",
                },
            },
            "B2/drive": {
                "RF_inputs": {
                    "port": ("octave2", 4),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con2", 7),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 71108093.0,
                "operations": {
                    "1856827432065012623": "1856827432065012623",
                },
            },
        },
        "pulses": {
            "5243483685427185520_B1/acquisition": {
                "length": 2000.0,
                "waveforms": {
                    "I": "640872628862575406_i",
                    "Q": "640872628862575406_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_B1/acquisition",
                    "sin": "sine_weights_B1/acquisition",
                    "minus_sin": "minus_sine_weights_B1/acquisition",
                },
            },
            "-1121073335717786507_B2/acquisition": {
                "length": 2000.0,
                "waveforms": {
                    "I": "-3753937565780980795_i",
                    "Q": "-3753937565780980795_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_B2/acquisition",
                    "sin": "sine_weights_B2/acquisition",
                    "minus_sin": "minus_sine_weights_B2/acquisition",
                },
            },
            "5983976435576360180_B3/acquisition": {
                "length": 2000.0,
                "waveforms": {
                    "I": "3154375928795754297_i",
                    "Q": "3154375928795754297_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_B3/acquisition",
                    "sin": "sine_weights_B3/acquisition",
                    "minus_sin": "minus_sine_weights_B3/acquisition",
                },
            },
            "7972844559298627969_B4/acquisition": {
                "length": 2000.0,
                "waveforms": {
                    "I": "-7439311533714691400_i",
                    "Q": "-7439311533714691400_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_B4/acquisition",
                    "sin": "sine_weights_B4/acquisition",
                    "minus_sin": "minus_sine_weights_B4/acquisition",
                },
            },
            "-1121073335717786507_B5/acquisition": {
                "length": 2000.0,
                "waveforms": {
                    "I": "-3753937565780980795_i",
                    "Q": "-3753937565780980795_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_B5/acquisition",
                    "sin": "sine_weights_B5/acquisition",
                    "minus_sin": "minus_sine_weights_B5/acquisition",
                },
            },
            "7712590452798127843": {
                "length": 40,
                "waveforms": {
                    "I": "7712590452798127843_i",
                    "Q": "7712590452798127843_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "1856827432065012623": {
                "length": 40,
                "waveforms": {
                    "I": "1856827432065012623_i",
                    "Q": "1856827432065012623_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "-5844443819135643270": {
                "length": 40,
                "waveforms": {
                    "I": "-5844443819135643270_i",
                    "Q": "-5844443819135643270_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "-7160365892553629488": {
                "length": 40,
                "waveforms": {
                    "I": "-7160365892553629488_i",
                    "Q": "-7160365892553629488_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "7080144445739131682": {
                "length": 40,
                "waveforms": {
                    "I": "7080144445739131682_i",
                    "Q": "7080144445739131682_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
        },
        "waveforms": {
            "640872628862575406_i": {
                "sample": 0.0045,
                "type": "constant",
            },
            "640872628862575406_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "-3753937565780980795_i": {
                "sample": 0.004,
                "type": "constant",
            },
            "-3753937565780980795_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "3154375928795754297_i": {
                "sample": 0.00365,
                "type": "constant",
            },
            "3154375928795754297_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "-7439311533714691400_i": {
                "sample": 0.003,
                "type": "constant",
            },
            "-7439311533714691400_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "7712590452798127843_i": {
                "samples": [
                    0.002346461843067531,
                    0.003157509534610567,
                    0.004183020506993152,
                    0.005455687240314252,
                    0.0070052410820625015,
                    0.008855454482795662,
                    0.011020791167246607,
                    0.013502955601261753,
                    0.01628767350283039,
                    0.019342090861463084,
                    0.02261319521362309,
                    0.026027628147804457,
                    0.029493166572683208,
                    0.032902004892907,
                    0.036135783060215136,
                    0.03907209756214237,
                    0.041592031353198555,
                    0.04358807461374575,
                    0.04497170862831118,
                ]
                + [0.04567990999043517] * 2
                + [
                    0.04497170862831118,
                    0.04358807461374575,
                    0.041592031353198555,
                    0.03907209756214237,
                    0.036135783060215136,
                    0.032902004892907,
                    0.029493166572683208,
                    0.026027628147804457,
                    0.02261319521362309,
                    0.019342090861463084,
                    0.01628767350283039,
                    0.013502955601261753,
                    0.011020791167246607,
                    0.008855454482795662,
                    0.0070052410820625015,
                    0.005455687240314252,
                    0.004183020506993152,
                    0.003157509534610567,
                    0.002346461843067531,
                ],
                "type": "arbitrary",
            },
            "7712590452798127843_q": {
                "samples": [
                    0.000464709435326265,
                    0.0005932664399014385,
                    0.0007434665354226111,
                    0.0009142538383182867,
                    0.0011027781859653078,
                    0.001304104039067955,
                    0.0015110537889467027,
                    0.0017142424103164333,
                    0.0019023493661508937,
                    0.0020626526582732114,
                    0.0021818200069394153,
                    0.002246916336197182,
                    0.0022465497975286035,
                    0.002172046416758314,
                    0.002018522256879205,
                    0.0017857169588947881,
                    0.0014784667395082297,
                    0.0011067284569896384,
                    0.0006851158736344282,
                    0.00023196829292017858,
                    -0.00023196829292017858,
                    -0.0006851158736344282,
                    -0.0011067284569896384,
                    -0.0014784667395082297,
                    -0.0017857169588947881,
                    -0.002018522256879205,
                    -0.002172046416758314,
                    -0.0022465497975286035,
                    -0.002246916336197182,
                    -0.0021818200069394153,
                    -0.0020626526582732114,
                    -0.0019023493661508937,
                    -0.0017142424103164333,
                    -0.0015110537889467027,
                    -0.001304104039067955,
                    -0.0011027781859653078,
                    -0.0009142538383182867,
                    -0.0007434665354226111,
                    -0.0005932664399014385,
                    -0.000464709435326265,
                ],
                "type": "arbitrary",
            },
            "1856827432065012623_i": {
                "samples": [
                    0.0025809995970196707,
                    0.0034731145790812237,
                    0.004601129259685824,
                    0.006001003856217911,
                    0.007705441477024947,
                    0.009740590719191953,
                    0.012122361011554197,
                    0.014852627187779108,
                    0.017915688197271632,
                    0.021275406146682146,
                    0.024873469775834156,
                    0.028629188221974328,
                    0.032441120346289216,
                    0.036190684975604015,
                    0.03974769152626758,
                    0.04297750179085285,
                    0.045749312514495245,
                    0.04794486786363794,
                    0.049466801341724036,
                ]
                + [0.050245790113968986] * 2
                + [
                    0.049466801341724036,
                    0.04794486786363794,
                    0.045749312514495245,
                    0.04297750179085285,
                    0.03974769152626758,
                    0.036190684975604015,
                    0.032441120346289216,
                    0.028629188221974328,
                    0.024873469775834156,
                    0.021275406146682146,
                    0.017915688197271632,
                    0.014852627187779108,
                    0.012122361011554197,
                    0.009740590719191953,
                    0.007705441477024947,
                    0.006001003856217911,
                    0.004601129259685824,
                    0.0034731145790812237,
                    0.0025809995970196707,
                ],
                "type": "arbitrary",
            },
            "1856827432065012623_q": {
                "samples": [
                    -0.00038174683870124276,
                    -0.000487353108681576,
                    -0.0006107386207437012,
                    -0.0007510359937138923,
                    -0.0009059038923653074,
                    -0.0010712878982157747,
                    -0.0012412917904990432,
                    -0.0014082060125300637,
                    -0.0015627310345518424,
                    -0.00169441606254817,
                    -0.00179230897190516,
                    -0.0018457839306990575,
                    -0.0018454828286181561,
                    -0.001784280219160388,
                    -0.0016581640737953463,
                    -0.001466920514309501,
                    -0.0012145223682319781,
                    -0.0009091489383250319,
                    -0.0005628050541309958,
                    -0.00019055598137152158,
                    0.00019055598137152158,
                    0.0005628050541309958,
                    0.0009091489383250319,
                    0.0012145223682319781,
                    0.001466920514309501,
                    0.0016581640737953463,
                    0.001784280219160388,
                    0.0018454828286181561,
                    0.0018457839306990575,
                    0.00179230897190516,
                    0.00169441606254817,
                    0.0015627310345518424,
                    0.0014082060125300637,
                    0.0012412917904990432,
                    0.0010712878982157747,
                    0.0009059038923653074,
                    0.0007510359937138923,
                    0.0006107386207437012,
                    0.000487353108681576,
                    0.00038174683870124276,
                ],
                "type": "arbitrary",
            },
            "-5844443819135643270_i": {
                "samples": [
                    0.003414157800018717,
                    0.004594251484665579,
                    0.006086394344652421,
                    0.007938154716222001,
                    0.010192792417228716,
                    0.012884896928740466,
                    0.016035513314311113,
                    0.019647121612293546,
                    0.023698952402801187,
                    0.02814320231903059,
                    0.032902736965459034,
                    0.03787081810827292,
                    0.04291325895576461,
                    0.047873199802183825,
                    0.052578423961726045,
                    0.05685083141198195,
                    0.06051739502292818,
                    0.06342168544951488,
                    0.06543490585501874,
                ]
                + [0.0664653556838208] * 2
                + [
                    0.06543490585501874,
                    0.06342168544951488,
                    0.06051739502292818,
                    0.05685083141198195,
                    0.052578423961726045,
                    0.047873199802183825,
                    0.04291325895576461,
                    0.03787081810827292,
                    0.032902736965459034,
                    0.02814320231903059,
                    0.023698952402801187,
                    0.019647121612293546,
                    0.016035513314311113,
                    0.012884896928740466,
                    0.010192792417228716,
                    0.007938154716222001,
                    0.006086394344652421,
                    0.004594251484665579,
                    0.003414157800018717,
                ],
                "type": "arbitrary",
            },
            "-5844443819135643270_q": {
                "samples": [
                    -0.0006277520724865696,
                    -0.0008014131172597861,
                    -0.0010043107003159563,
                    -0.0012350184828508214,
                    -0.0014896863267832496,
                    -0.0017616470659526234,
                    -0.002041204837995171,
                    -0.0023156818949995875,
                    -0.0025697859058022017,
                    -0.002786331377459247,
                    -0.002947308419049586,
                    -0.003035243701822876,
                    -0.0030347485635894875,
                    -0.0029341057788072732,
                    -0.0027267178881929875,
                    -0.0024122331861706025,
                    -0.001997184669119406,
                    -0.001495022544716217,
                    -0.0009254877927440936,
                    -0.00031335403493492085,
                    0.00031335403493492085,
                    0.0009254877927440936,
                    0.001495022544716217,
                    0.001997184669119406,
                    0.0024122331861706025,
                    0.0027267178881929875,
                    0.0029341057788072732,
                    0.0030347485635894875,
                    0.003035243701822876,
                    0.002947308419049586,
                    0.002786331377459247,
                    0.0025697859058022017,
                    0.0023156818949995875,
                    0.002041204837995171,
                    0.0017616470659526234,
                    0.0014896863267832496,
                    0.0012350184828508214,
                    0.0010043107003159563,
                    0.0008014131172597861,
                    0.0006277520724865696,
                ],
                "type": "arbitrary",
            },
            "-7160365892553629488_i": {
                "samples": [
                    0.00406488731572278,
                    0.005469903759326908,
                    0.007246445132070012,
                    0.009451146170232343,
                    0.012135511899409337,
                    0.01534072446497505,
                    0.01909184006436072,
                    0.02339181142472006,
                    0.028215910529248624,
                    0.03350722281489749,
                    0.03917391227280832,
                    0.045088896641953466,
                    0.051092413480319586,
                    0.0569977060339427,
                    0.06259973356871297,
                    0.06768645066540062,
                    0.07205185167713603,
                    0.07550969223627559,
                    0.07790662716706351,
                ]
                + [0.07913347802866201] * 2
                + [
                    0.07790662716706351,
                    0.07550969223627559,
                    0.07205185167713603,
                    0.06768645066540062,
                    0.06259973356871297,
                    0.0569977060339427,
                    0.051092413480319586,
                    0.045088896641953466,
                    0.03917391227280832,
                    0.03350722281489749,
                    0.028215910529248624,
                    0.02339181142472006,
                    0.01909184006436072,
                    0.01534072446497505,
                    0.012135511899409337,
                    0.009451146170232343,
                    0.007246445132070012,
                    0.005469903759326908,
                    0.00406488731572278,
                ],
                "type": "arbitrary",
            },
            "-7160365892553629488_q": {
                "samples": [
                    -0.0006897617096362667,
                    -0.0008805770719265391,
                    -0.0011035169711379185,
                    -0.0013570141740659823,
                    -0.0016368382242270781,
                    -0.0019356633697345403,
                    -0.00224283598650085,
                    -0.002544426012871249,
                    -0.0028236305342078044,
                    -0.0030615664667050266,
                    -0.003238444894170379,
                    -0.003335066464439031,
                    -0.0033345224162242386,
                    -0.003223938091079824,
                    -0.0029960643296737567,
                    -0.0026505146847921736,
                    -0.0021944674851879778,
                    -0.0016427015562107633,
                    -0.001016907900665383,
                    -0.00034430728998151994,
                    0.00034430728998151994,
                    0.001016907900665383,
                    0.0016427015562107633,
                    0.0021944674851879778,
                    0.0026505146847921736,
                    0.0029960643296737567,
                    0.003223938091079824,
                    0.0033345224162242386,
                    0.003335066464439031,
                    0.003238444894170379,
                    0.0030615664667050266,
                    0.0028236305342078044,
                    0.002544426012871249,
                    0.00224283598650085,
                    0.0019356633697345403,
                    0.0016368382242270781,
                    0.0013570141740659823,
                    0.0011035169711379185,
                    0.0008805770719265391,
                    0.0006897617096362667,
                ],
                "type": "arbitrary",
            },
            "7080144445739131682_i": {
                "samples": [
                    0.0032310298144705048,
                    0.0043478258450879124,
                    0.005759933413179916,
                    0.007512369393076185,
                    0.009646073240256884,
                    0.012193779131389783,
                    0.015175403318673173,
                    0.018593292816606263,
                    0.022427792231732302,
                    0.026633662265688123,
                    0.03113790584386466,
                    0.03583950993874638,
                    0.0406114852457636,
                    0.045305385672013,
                    0.04975823185948696,
                    0.05380147668292982,
                    0.05727137381057722,
                    0.060019884426615946,
                    0.061925120076019066,
                ]
                + [0.06290029882117174] * 2
                + [
                    0.061925120076019066,
                    0.060019884426615946,
                    0.05727137381057722,
                    0.05380147668292982,
                    0.04975823185948696,
                    0.045305385672013,
                    0.0406114852457636,
                    0.03583950993874638,
                    0.03113790584386466,
                    0.026633662265688123,
                    0.022427792231732302,
                    0.018593292816606263,
                    0.015175403318673173,
                    0.012193779131389783,
                    0.009646073240256884,
                    0.007512369393076185,
                    0.005759933413179916,
                    0.0043478258450879124,
                    0.0032310298144705048,
                ],
                "type": "arbitrary",
            },
            "7080144445739131682_q": {
                "samples": [
                    -0.00014766815948947227,
                    -0.00018851901125185869,
                    -0.00023624726889995748,
                    -0.0002905174101228681,
                    -0.00035042375443120706,
                    -0.0004143979626683246,
                    -0.00048015924562989335,
                    -0.0005447253754865116,
                    -0.0006044990874959096,
                    -0.0006554377823196686,
                    -0.000693304934804799,
                    -0.0007139902370609629,
                    -0.0007138737640856883,
                    -0.0006901992348470731,
                    -0.0006414147075636991,
                    -0.0005674374493902754,
                    -0.0004698042382898912,
                    -0.00035167901031220284,
                    -0.0002177055002672545,
                    -7.371128768106063e-05,
                    7.371128768106063e-05,
                    0.0002177055002672545,
                    0.00035167901031220284,
                    0.0004698042382898912,
                    0.0005674374493902754,
                    0.0006414147075636991,
                    0.0006901992348470731,
                    0.0007138737640856883,
                    0.0007139902370609629,
                    0.000693304934804799,
                    0.0006554377823196686,
                    0.0006044990874959096,
                    0.0005447253754865116,
                    0.00048015924562989335,
                    0.0004143979626683246,
                    0.00035042375443120706,
                    0.0002905174101228681,
                    0.00023624726889995748,
                    0.00018851901125185869,
                    0.00014766815948947227,
                ],
                "type": "arbitrary",
            },
        },
        "digital_waveforms": {
            "ON": {
                "samples": [(1, 0)],
            },
        },
        "integration_weights": {
            "cosine_weights_B1/acquisition": {
                "cosine": [(1.0, 2000.0)],
                "sine": [(-0.0, 2000.0)],
            },
            "sine_weights_B1/acquisition": {
                "cosine": [(0.0, 2000.0)],
                "sine": [(1.0, 2000.0)],
            },
            "minus_sine_weights_B1/acquisition": {
                "cosine": [(-0.0, 2000.0)],
                "sine": [(-1.0, 2000.0)],
            },
            "cosine_weights_B2/acquisition": {
                "cosine": [(1.0, 2000.0)],
                "sine": [(-0.0, 2000.0)],
            },
            "sine_weights_B2/acquisition": {
                "cosine": [(0.0, 2000.0)],
                "sine": [(1.0, 2000.0)],
            },
            "minus_sine_weights_B2/acquisition": {
                "cosine": [(-0.0, 2000.0)],
                "sine": [(-1.0, 2000.0)],
            },
            "cosine_weights_B3/acquisition": {
                "cosine": [(1.0, 2000.0)],
                "sine": [(-0.0, 2000.0)],
            },
            "sine_weights_B3/acquisition": {
                "cosine": [(0.0, 2000.0)],
                "sine": [(1.0, 2000.0)],
            },
            "minus_sine_weights_B3/acquisition": {
                "cosine": [(-0.0, 2000.0)],
                "sine": [(-1.0, 2000.0)],
            },
            "cosine_weights_B4/acquisition": {
                "cosine": [(1.0, 2000.0)],
                "sine": [(-0.0, 2000.0)],
            },
            "sine_weights_B4/acquisition": {
                "cosine": [(0.0, 2000.0)],
                "sine": [(1.0, 2000.0)],
            },
            "minus_sine_weights_B4/acquisition": {
                "cosine": [(-0.0, 2000.0)],
                "sine": [(-1.0, 2000.0)],
            },
            "cosine_weights_B5/acquisition": {
                "cosine": [(1.0, 2000.0)],
                "sine": [(-0.0, 2000.0)],
            },
            "sine_weights_B5/acquisition": {
                "cosine": [(0.0, 2000.0)],
                "sine": [(1.0, 2000.0)],
            },
            "minus_sine_weights_B5/acquisition": {
                "cosine": [(-0.0, 2000.0)],
                "sine": [(-1.0, 2000.0)],
            },
        },
        "mixers": {},
    }

    _run_until_success(
        _calibrate_readout_mixer,
        platform,
        controller,
        config,
        ["B1", "B2", "B3", "B4", "B5"],
        label="readout",
    )
    _run_until_success(
        _calibrate_drive_mixers,
        platform,
        controller,
        config,
        ["B1", "B2", "B3", "B4", "B5"],
        label="drive",
    )

    controller.disconnect()
