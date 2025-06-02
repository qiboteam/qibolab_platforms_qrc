import warnings

from qibolab import create_platform

# from qibolab.instruments.qm.controller import controllers_config


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

    platform = create_platform("qw5q_platinum")
    controller = platform.instruments["qm"]
    controller.write_calibration = True
    controller.connect()

    # config = controllers_config(
    #    list(platform.qubits.values()), controller.time_of_flight, controller.smearing
    # )
    config = {
        "version": 1,
        "controllers": {
            "con1": {
                "type": "opx1000",
                "fems": {
                    "4": {
                        "type": "LF",
                        "analog_outputs": {
                            "4": {
                                "offset": 0.47542516543032876,
                                "filter": {},
                                "output_mode": "amplified",
                                "sampling_rate": 1000000000.0,
                                "upsampling_mode": "pulse",
                            },
                            "1": {
                                "offset": 0.3612981245395635,
                                "filter": {},
                                "output_mode": "amplified",
                                "sampling_rate": 1000000000.0,
                                "upsampling_mode": "pulse",
                            },
                            "3": {
                                "offset": 0.5347210367348649,
                                "filter": {
                                    "feedforward": [
                                        1.2636351569036441,
                                        -0.8232188600289677,
                                        -0.023584638849310263,
                                        -0.021177265809741615,
                                        0.0019818771228793768,
                                        0.018566245435279526,
                                        -0.00871919444276136,
                                        0.0029207057818416583,
                                        -0.0026753197501048864,
                                        -0.009824924082361835,
                                        -0.00796679653743725,
                                        0.011947706348409613,
                                        0.003341842518842916,
                                        -0.004751172959027721,
                                        0.0023062425297495108,
                                        0.008316586034492656,
                                        -0.00771451388109923,
                                        0.00015556469587163935,
                                        0.0008330091025414715,
                                        -0.004488698619546089,
                                        0.005365344729781505,
                                        -0.0006837922723672002,
                                        0.0037696780547130616,
                                        -0.00911021303345722,
                                        0.00036562761421022683,
                                        0.0023091143796012716,
                                        -0.008705373420043074,
                                        0.006767549541320114,
                                        0.00589556012888095,
                                        -0.011731828850264376,
                                        0.005008575336492184,
                                    ],
                                    "feedback": [0.5874633945103754],
                                },
                                "output_mode": "amplified",
                                "sampling_rate": 1000000000.0,
                                "upsampling_mode": "pulse",
                            },
                            "2": {
                                "offset": 0.8036553966185815,
                                "filter": {
                                    "feedforward": [
                                        1.2234520961227922,
                                        -0.6969389285337555,
                                        -0.02769138330673253,
                                        -0.024860121491298535,
                                        -0.014292774551705262,
                                        0.021421949905432187,
                                        -0.0011777971109444671,
                                        -0.0040987595190198,
                                        -0.008531719373108315,
                                        0.0002077367545341895,
                                        -0.005295525394849506,
                                        0.004158710161347265,
                                        0.0038254634052596803,
                                        -0.0014707735693399151,
                                        0.007813406095929058,
                                        -0.0022362981062549496,
                                        -0.0026825389313108704,
                                        -0.008546084311691708,
                                        0.004949281082275419,
                                        -0.003016595671100195,
                                        0.0008142471401767621,
                                        -0.0026335679848660267,
                                        0.002497669374809954,
                                        -0.0021172027048112947,
                                        -0.0010707770484308118,
                                        -0.004577738364072215,
                                        0.0013221649026706503,
                                        0.009149085842958002,
                                        -0.010857175640066214,
                                        0.003358522719122027,
                                        0.00021572576825085632,
                                    ],
                                    "feedback": [0.5091791853685043],
                                },
                                "output_mode": "amplified",
                                "sampling_rate": 1000000000.0,
                                "upsampling_mode": "pulse",
                            },
                            "5": {
                                "offset": -0.07458798541755325,
                                "filter": {
                                    "feedforward": [
                                        1.2381134243279095,
                                        -1.0529559918952465,
                                        0.35306911939962116,
                                        -0.1638040790979965,
                                        -0.003226904445920352,
                                        0.02526132654819567,
                                        -0.0018251092763359004,
                                        -0.004035743016841075,
                                        -0.010524269759444803,
                                        -0.007939220124088072,
                                        -0.015375126663621137,
                                        0.01923982395182343,
                                        0.006046019934125838,
                                        0.004704896045249214,
                                        0.0020939935701098037,
                                        0.004295117900596931,
                                        0.003824449652170595,
                                        -0.026540394249118505,
                                        -0.01495546551537057,
                                        0.009664533684332425,
                                        -0.00015299699362413943,
                                        0.014765621765855335,
                                        -0.012132948560529487,
                                        0.014667660315440907,
                                        0.0016430974676778995,
                                        -0.007047402321197055,
                                        -0.0213316020466652,
                                        0.010012067579274909,
                                        0.006614372986725079,
                                        -0.012248690590664094,
                                        0.00696600204623011,
                                    ],
                                    "feedback": [0.6136716461257441],
                                },
                                "output_mode": "amplified",
                                "sampling_rate": 1000000000.0,
                                "upsampling_mode": "pulse",
                            },
                        },
                        "digital_outputs": {},
                        "analog_inputs": {},
                    },
                    "2": {
                        "type": "LF",
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
                        },
                        "digital_outputs": {
                            "1": {},
                            "3": {},
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
                    "1": {
                        "type": "LF",
                        "analog_outputs": {
                            "3": {
                                "offset": 0,
                            },
                            "4": {
                                "offset": 0,
                            },
                            "5": {
                                "offset": 0,
                            },
                            "6": {
                                "offset": 0,
                            },
                            "1": {
                                "offset": 0,
                            },
                            "2": {
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
                            "3": {},
                            "5": {},
                            "1": {},
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
            },
        },
        "octaves": {
            "octave2": {
                "connectivity": ("con1", 2),
                "RF_outputs": {
                    "1": {
                        "LO_frequency": 7550000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                    "2": {
                        "LO_frequency": 6500000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                },
                "RF_inputs": {
                    "1": {
                        "LO_frequency": 7550000000.0,
                        "LO_source": "internal",
                        "IF_mode_I": "direct",
                        "IF_mode_Q": "direct",
                    },
                },
            },
            "octave1": {
                "connectivity": ("con1", 1),
                "RF_outputs": {
                    "2": {
                        "LO_frequency": 4900000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                    "3": {
                        "LO_frequency": 4900000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                    "1": {
                        "LO_frequency": 5700000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                    "4": {
                        "LO_frequency": 6500000000.0,
                        "gain": -10.0,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                    },
                },
                "RF_inputs": {},
            },
        },
        "elements": {
            "0/flux": {
                "singleInput": {
                    "port": ("con1", 4, 4),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "1/flux": {
                "singleInput": {
                    "port": ("con1", 4, 1),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "2/flux": {
                "singleInput": {
                    "port": ("con1", 4, 3),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "3/flux": {
                "singleInput": {
                    "port": ("con1", 4, 2),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "4/flux": {
                "singleInput": {
                    "port": ("con1", 4, 5),
                },
                "intermediate_frequency": 0,
                "operations": {},
            },
            "3/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 113563718.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-7052453462689321490": "-7052453462689321490_3/acquisition",
                },
            },
            "4/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": 246304249.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "6899405388814963075": "6899405388814963075_4/acquisition",
                },
            },
            "0/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -344529483.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-165724088523851233": "-165724088523851233_0/acquisition",
                },
            },
            "2/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -50037942.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-6955925623468422567": "-6955925623468422567_2/acquisition",
                },
            },
            "1/acquisition": {
                "RF_inputs": {
                    "port": ("octave2", 1),
                },
                "RF_outputs": {
                    "port": ("octave2", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -211216529.0,
                "time_of_flight": 308.0,
                "smearing": 0.0,
                "operations": {
                    "-3879620943297864987": "-3879620943297864987_1/acquisition",
                },
            },
            "0/drive": {
                "RF_inputs": {
                    "port": ("octave1", 2),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 1, 3),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -124585847.0,
                "operations": {
                    "3370224418967753926": "3370224418967753926",
                },
            },
            "1/drive": {
                "RF_inputs": {
                    "port": ("octave1", 3),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 1, 5),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -81741901.0,
                "operations": {
                    "7131483082705864780": "7131483082705864780",
                },
            },
            "2/drive": {
                "RF_inputs": {
                    "port": ("octave1", 1),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 1, 1),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -178127360.0,
                "operations": {
                    "-6101512857637796550": "-6101512857637796550",
                },
            },
            "4/drive": {
                "RF_inputs": {
                    "port": ("octave2", 2),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 2, 3),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -255993015.0,
                "operations": {
                    "-2577896379486814566": "-2577896379486814566",
                },
            },
            "3/drive": {
                "RF_inputs": {
                    "port": ("octave1", 4),
                },
                "digitalInputs": {
                    "output_switch": {
                        "port": ("con1", 1, 7),
                        "delay": 57,
                        "buffer": 18,
                    },
                },
                "intermediate_frequency": -165182626.0,
                "operations": {
                    "-6915881298201868187": "-6915881298201868187",
                },
            },
        },
        "pulses": {
            "-165724088523851233_0/acquisition": {
                "length": 1000.0,
                "waveforms": {
                    "I": "-3855307660189368854_i",
                    "Q": "-3855307660189368854_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_0/acquisition",
                    "sin": "sine_weights_0/acquisition",
                    "minus_sin": "minus_sine_weights_0/acquisition",
                },
            },
            "-3879620943297864987_1/acquisition": {
                "length": 1000.0,
                "waveforms": {
                    "I": "-6994239688333363449_i",
                    "Q": "-6994239688333363449_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_1/acquisition",
                    "sin": "sine_weights_1/acquisition",
                    "minus_sin": "minus_sine_weights_1/acquisition",
                },
            },
            "-6955925623468422567_2/acquisition": {
                "length": 1000.0,
                "waveforms": {
                    "I": "-8292474260899565991_i",
                    "Q": "-8292474260899565991_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_2/acquisition",
                    "sin": "sine_weights_2/acquisition",
                    "minus_sin": "minus_sine_weights_2/acquisition",
                },
            },
            "-7052453462689321490_3/acquisition": {
                "length": 1000.0,
                "waveforms": {
                    "I": "1966294731927376108_i",
                    "Q": "1966294731927376108_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_3/acquisition",
                    "sin": "sine_weights_3/acquisition",
                    "minus_sin": "minus_sine_weights_3/acquisition",
                },
            },
            "6899405388814963075_4/acquisition": {
                "length": 1000.0,
                "waveforms": {
                    "I": "-6221680348955233409_i",
                    "Q": "-6221680348955233409_q",
                },
                "digital_marker": "ON",
                "operation": "measurement",
                "integration_weights": {
                    "cos": "cosine_weights_4/acquisition",
                    "sin": "sine_weights_4/acquisition",
                    "minus_sin": "minus_sine_weights_4/acquisition",
                },
            },
            "3370224418967753926": {
                "length": 40,
                "waveforms": {
                    "I": "3370224418967753926_i",
                    "Q": "3370224418967753926_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "7131483082705864780": {
                "length": 40,
                "waveforms": {
                    "I": "7131483082705864780_i",
                    "Q": "7131483082705864780_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "-6101512857637796550": {
                "length": 40,
                "waveforms": {
                    "I": "-6101512857637796550_i",
                    "Q": "-6101512857637796550_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "-6915881298201868187": {
                "length": 40,
                "waveforms": {
                    "I": "-6915881298201868187_i",
                    "Q": "-6915881298201868187_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
            "-2577896379486814566": {
                "length": 40,
                "waveforms": {
                    "I": "-2577896379486814566_i",
                    "Q": "-2577896379486814566_q",
                },
                "digital_marker": "ON",
                "operation": "control",
            },
        },
        "waveforms": {
            "-3855307660189368854_i": {
                "sample": 0.0075,
                "type": "constant",
            },
            "-3855307660189368854_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "-6994239688333363449_i": {
                "sample": 0.0035,
                "type": "constant",
            },
            "-6994239688333363449_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "-8292474260899565991_i": {
                "sample": 0.004,
                "type": "constant",
            },
            "-8292474260899565991_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "1966294731927376108_i": {
                "sample": 0.005,
                "type": "constant",
            },
            "1966294731927376108_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "-6221680348955233409_i": {
                "sample": 0.006,
                "type": "constant",
            },
            "-6221680348955233409_q": {
                "sample": 0.0,
                "type": "constant",
            },
            "3370224418967753926_i": {
                "samples": [
                    0.1140017787920408,
                    0.1178249634757914,
                    0.12156512930497032,
                    0.12520645961595825,
                    0.12873317218030897,
                    0.13212963132214406,
                    0.13538046200280773,
                    0.138470664725382,
                    0.14138573007032212,
                    0.14411175164772863,
                    0.14663553624242812,
                    0.14894470993562628,
                    0.15102781901167525,
                    0.15287442450041827,
                    0.15447518926429454,
                    0.15582195661426362,
                    0.15690781952870178,
                    0.15772717965352587,
                    0.15827579537843223,
                ]
                + [0.158550818411602] * 2
                + [
                    0.15827579537843223,
                    0.15772717965352587,
                    0.15690781952870178,
                    0.15582195661426362,
                    0.15447518926429454,
                    0.15287442450041827,
                    0.15102781901167525,
                    0.14894470993562628,
                    0.14663553624242812,
                    0.14411175164772863,
                    0.14138573007032212,
                    0.138470664725382,
                    0.13538046200280773,
                    0.13212963132214406,
                    0.12873317218030897,
                    0.12520645961595825,
                    0.12156512930497032,
                    0.1178249634757914,
                    0.1140017787920408,
                ],
                "type": "arbitrary",
            },
            "3370224418967753926_q": {
                "samples": [
                    -0.003087548175617772,
                    -0.0030274469781974176,
                    -0.002954708003940251,
                    -0.002869314699532377,
                    -0.0027713391233260966,
                    -0.002660943964126512,
                    -0.002538383662552645,
                    -0.002404004595926771,
                    -0.0022582442997343116,
                    -0.0021016297115293765,
                    -0.0019347744365320382,
                    -0.0017583750478511436,
                    -0.0015732064480382842,
                    -0.0013801163322954427,
                    -0.001180018806880028,
                    -0.0009738872288391476,
                    -0.0007627463449311892,
                    -0.0005476638182414092,
                    -0.0003297412403717338,
                    -0.00011010473500805696,
                    0.00011010473500805696,
                    0.0003297412403717338,
                    0.0005476638182414092,
                    0.0007627463449311892,
                    0.0009738872288391476,
                    0.001180018806880028,
                    0.0013801163322954427,
                    0.0015732064480382842,
                    0.0017583750478511436,
                    0.0019347744365320382,
                    0.0021016297115293765,
                    0.0022582442997343116,
                    0.002404004595926771,
                    0.002538383662552645,
                    0.002660943964126512,
                    0.0027713391233260966,
                    0.002869314699532377,
                    0.002954708003940251,
                    0.0030274469781974176,
                    0.003087548175617772,
                ],
                "type": "arbitrary",
            },
            "7131483082705864780_i": {
                "samples": [
                    0.05463947185395496,
                    0.056471871261523206,
                    0.0582644808832146,
                    0.060009720011466414,
                    0.061700024443016956,
                    0.06332790021521817,
                    0.06488597828522893,
                    0.06636706960215583,
                    0.06776422000239515,
                    0.06907076434609075,
                    0.0702803793081439,
                    0.0713871342408503,
                    0.07238553953711435,
                    0.07327059194328414,
                    0.0740378162987933,
                    0.0746833032156834,
                    0.07520374225426127,
                    0.07559645020104029,
                    0.07585939411101505,
                ]
                + [0.07599120883741053] * 2
                + [
                    0.07585939411101505,
                    0.07559645020104029,
                    0.07520374225426127,
                    0.0746833032156834,
                    0.0740378162987933,
                    0.07327059194328414,
                    0.07238553953711435,
                    0.0713871342408503,
                    0.0702803793081439,
                    0.06907076434609075,
                    0.06776422000239515,
                    0.06636706960215583,
                    0.06488597828522893,
                    0.06332790021521817,
                    0.061700024443016956,
                    0.060009720011466414,
                    0.0582644808832146,
                    0.056471871261523206,
                    0.05463947185395496,
                ],
                "type": "arbitrary",
            },
            "7131483082705864780_q": {
                "samples": [
                    -0.004994389224150571,
                    -0.004897170085960215,
                    -0.004779508197451198,
                    -0.004641376782136856,
                    -0.004482892400937951,
                    -0.004304318217753111,
                    -0.004106065813362144,
                    -0.0038886954845013177,
                    -0.003652914984504114,
                    -0.0033995766826591545,
                    -0.0031296731410657835,
                    -0.0028443311299088795,
                    -0.002544804124351677,
                    -0.002232463348271939,
                    -0.0019087874514532649,
                    -0.0015753509272058216,
                    -0.001233811396358974,
                    -0.0008858959007934409,
                    -0.0005333863648430746,
                    -0.00017810439571268097,
                    0.00017810439571268097,
                    0.0005333863648430746,
                    0.0008858959007934409,
                    0.001233811396358974,
                    0.0015753509272058216,
                    0.0019087874514532649,
                    0.002232463348271939,
                    0.002544804124351677,
                    0.0028443311299088795,
                    0.0031296731410657835,
                    0.0033995766826591545,
                    0.003652914984504114,
                    0.0038886954845013177,
                    0.004106065813362144,
                    0.004304318217753111,
                    0.004482892400937951,
                    0.004641376782136856,
                    0.004779508197451198,
                    0.004897170085960215,
                    0.004994389224150571,
                ],
                "type": "arbitrary",
            },
            "-6101512857637796550_i": {
                "samples": [
                    0.05995704441234495,
                    0.06196777491417669,
                    0.06393484324509006,
                    0.06584993093485482,
                    0.06770473762375812,
                    0.06949104002859338,
                    0.0712007519432918,
                    0.07282598467074351,
                    0.0743591072606137,
                    0.07579280591441913,
                    0.0771201419142163,
                    0.07833460743524523,
                    0.07943017861590428,
                    0.08040136528047914,
                    0.08124325674093194,
                    0.08195156314343545,
                    0.08252265187272143,
                    0.08295357858206161,
                    0.08324211247804164,
                ]
                + [0.0833867555563243] * 2
                + [
                    0.08324211247804164,
                    0.08295357858206161,
                    0.08252265187272143,
                    0.08195156314343545,
                    0.08124325674093194,
                    0.08040136528047914,
                    0.07943017861590428,
                    0.07833460743524523,
                    0.0771201419142163,
                    0.07579280591441913,
                    0.0743591072606137,
                    0.07282598467074351,
                    0.0712007519432918,
                    0.06949104002859338,
                    0.06770473762375812,
                    0.06584993093485482,
                    0.06393484324509006,
                    0.06196777491417669,
                    0.05995704441234495,
                ],
                "type": "arbitrary",
            },
            "-6101512857637796550_q": {
                "samples": [
                    0.0014208570420633825,
                    0.001393199106143382,
                    0.0013597253988756133,
                    0.0013204283025999534,
                    0.001275340977808638,
                    0.0012245382921705257,
                    0.0011681373365696308,
                    0.001106297510189246,
                    0.0010392201622360072,
                    0.0009671477838037857,
                    0.0008903627495304485,
                    0.0008091856149994949,
                    0.0007239729821762109,
                    0.0006351149514343405,
                    0.0005430321848135208,
                    0.0004481726109406626,
                    0.0003510078074447352,
                    0.00025202910159480524,
                    0.0001517434342047634,
                    5.066903549429428e-05,
                    -5.066903549429428e-05,
                    -0.0001517434342047634,
                    -0.00025202910159480524,
                    -0.0003510078074447352,
                    -0.0004481726109406626,
                    -0.0005430321848135208,
                    -0.0006351149514343405,
                    -0.0007239729821762109,
                    -0.0008091856149994949,
                    -0.0008903627495304485,
                    -0.0009671477838037857,
                    -0.0010392201622360072,
                    -0.001106297510189246,
                    -0.0011681373365696308,
                    -0.0012245382921705257,
                    -0.001275340977808638,
                    -0.0013204283025999534,
                    -0.0013597253988756133,
                    -0.001393199106143382,
                    -0.0014208570420633825,
                ],
                "type": "arbitrary",
            },
            "-6915881298201868187_i": {
                "samples": [
                    0.08569448326782342,
                    0.08856834926695936,
                    0.0913798104692633,
                    0.09411697757940807,
                    0.09676798718678864,
                    0.09932108604352467,
                    0.10176471682124118,
                    0.10408760448413361,
                    0.10627884238474805,
                    0.1083279771695563,
                    0.11022509157438141,
                    0.11196088419543553,
                    0.11352674534035824,
                    0.11491482809515474,
                    0.11611811378707322,
                    0.1171304710797441,
                    0.11794670800462766,
                    0.11856261631106858,
                    0.11897500760492913,
                ]
                + [0.11918174084158527] * 2
                + [
                    0.11897500760492913,
                    0.11856261631106858,
                    0.11794670800462766,
                    0.1171304710797441,
                    0.11611811378707322,
                    0.11491482809515474,
                    0.11352674534035824,
                    0.11196088419543553,
                    0.11022509157438141,
                    0.1083279771695563,
                    0.10627884238474805,
                    0.10408760448413361,
                    0.10176471682124118,
                    0.09932108604352467,
                    0.09676798718678864,
                    0.09411697757940807,
                    0.0913798104692633,
                    0.08856834926695936,
                    0.08569448326782342,
                ],
                "type": "arbitrary",
            },
            "-6915881298201868187_q": {
                "samples": [
                    -0.0017406691913776629,
                    -0.0017067858973320292,
                    -0.001665777795012612,
                    -0.001617635552146076,
                    -0.001562399793120025,
                    -0.0015001622371157372,
                    -0.001431066330298704,
                    -0.001355307350053823,
                    -0.0012731319660672941,
                    -0.0011848372502920224,
                    -0.0010907691353714828,
                    -0.000991320328813752,
                    -0.0008869276979715487,
                    -0.0007780691485609434,
                    -0.000665260026905107,
                    -0.0005490490831863004,
                    -0.000430014039600205,
                    -0.00030875681331007444,
                    -0.00018589844938270175,
                    -6.207382335499233e-05,
                    6.207382335499233e-05,
                    0.00018589844938270175,
                    0.00030875681331007444,
                    0.000430014039600205,
                    0.0005490490831863004,
                    0.000665260026905107,
                    0.0007780691485609434,
                    0.0008869276979715487,
                    0.000991320328813752,
                    0.0010907691353714828,
                    0.0011848372502920224,
                    0.0012731319660672941,
                    0.001355307350053823,
                    0.001431066330298704,
                    0.0015001622371157372,
                    0.001562399793120025,
                    0.001617635552146076,
                    0.001665777795012612,
                    0.0017067858973320292,
                    0.0017406691913776629,
                ],
                "type": "arbitrary",
            },
            "-2577896379486814566_i": {
                "samples": [
                    0.09155390847443858,
                    0.09462427723820574,
                    0.09762797422988616,
                    0.1005522972145786,
                    0.10338457161199144,
                    0.10611224053701745,
                    0.10872295642019943,
                    0.11120467328661887,
                    0.11354573873854047,
                    0.1157349846664702,
                    0.11776181570578068,
                    0.1196162944621543,
                    0.12128922254899373,
                    0.12277221651361576,
                    0.12405777777620255,
                    0.1251393557656158,
                    0.126011403508534,
                    0.12666942501197553,
                    0.1271100138729383,
                ]
                + [0.12733088265125028] * 2
                + [
                    0.1271100138729383,
                    0.12666942501197553,
                    0.126011403508534,
                    0.1251393557656158,
                    0.12405777777620255,
                    0.12277221651361576,
                    0.12128922254899373,
                    0.1196162944621543,
                    0.11776181570578068,
                    0.1157349846664702,
                    0.11354573873854047,
                    0.11120467328661887,
                    0.10872295642019943,
                    0.10611224053701745,
                    0.10338457161199144,
                    0.1005522972145786,
                    0.09762797422988616,
                    0.09462427723820574,
                    0.09155390847443858,
                ],
                "type": "arbitrary",
            },
            "-2577896379486814566_q": {
                "samples": [
                    0.0012397925105913556,
                    0.001215659117296393,
                    0.0011864510757104221,
                    0.0011521617389170465,
                    0.0011128200416568525,
                    0.0010684913109630229,
                    0.0010192777164393697,
                    0.0009653183445018999,
                    0.0009067888857591773,
                    0.0008439009298596787,
                    0.0007769008675034143,
                    0.0007060684048113275,
                    0.0006317147007760091,
                    0.0005541801439850712,
                    0.00047383179011744036,
                    0.00039106048676754943,
                    0.0003062777168610201,
                    0.00021991219620134643,
                    0.0001324062644509774,
                    4.421211203168413e-05,
                    -4.421211203168413e-05,
                    -0.0001324062644509774,
                    -0.00021991219620134643,
                    -0.0003062777168610201,
                    -0.00039106048676754943,
                    -0.00047383179011744036,
                    -0.0005541801439850712,
                    -0.0006317147007760091,
                    -0.0007060684048113275,
                    -0.0007769008675034143,
                    -0.0008439009298596787,
                    -0.0009067888857591773,
                    -0.0009653183445018999,
                    -0.0010192777164393697,
                    -0.0010684913109630229,
                    -0.0011128200416568525,
                    -0.0011521617389170465,
                    -0.0011864510757104221,
                    -0.001215659117296393,
                    -0.0012397925105913556,
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
            "cosine_weights_0/acquisition": {
                "cosine": [(1.0, 1000.0)],
                "sine": [(-0.0, 1000.0)],
            },
            "sine_weights_0/acquisition": {
                "cosine": [(0.0, 1000.0)],
                "sine": [(1.0, 1000.0)],
            },
            "minus_sine_weights_0/acquisition": {
                "cosine": [(-0.0, 1000.0)],
                "sine": [(-1.0, 1000.0)],
            },
            "cosine_weights_1/acquisition": {
                "cosine": [(1.0, 1000.0)],
                "sine": [(-0.0, 1000.0)],
            },
            "sine_weights_1/acquisition": {
                "cosine": [(0.0, 1000.0)],
                "sine": [(1.0, 1000.0)],
            },
            "minus_sine_weights_1/acquisition": {
                "cosine": [(-0.0, 1000.0)],
                "sine": [(-1.0, 1000.0)],
            },
            "cosine_weights_2/acquisition": {
                "cosine": [(1.0, 1000.0)],
                "sine": [(-0.0, 1000.0)],
            },
            "sine_weights_2/acquisition": {
                "cosine": [(0.0, 1000.0)],
                "sine": [(1.0, 1000.0)],
            },
            "minus_sine_weights_2/acquisition": {
                "cosine": [(-0.0, 1000.0)],
                "sine": [(-1.0, 1000.0)],
            },
            "cosine_weights_3/acquisition": {
                "cosine": [(1.0, 1000.0)],
                "sine": [(-0.0, 1000.0)],
            },
            "sine_weights_3/acquisition": {
                "cosine": [(0.0, 1000.0)],
                "sine": [(1.0, 1000.0)],
            },
            "minus_sine_weights_3/acquisition": {
                "cosine": [(-0.0, 1000.0)],
                "sine": [(-1.0, 1000.0)],
            },
            "cosine_weights_4/acquisition": {
                "cosine": [(1.0, 1000.0)],
                "sine": [(-0.0, 1000.0)],
            },
            "sine_weights_4/acquisition": {
                "cosine": [(0.0, 1000.0)],
                "sine": [(1.0, 1000.0)],
            },
            "minus_sine_weights_4/acquisition": {
                "cosine": [(-0.0, 1000.0)],
                "sine": [(-1.0, 1000.0)],
            },
        },
        "mixers": {},
    }

    _run_until_success(
        _calibrate_readout_mixer,
        platform,
        controller,
        config,
        [0, 1],
        label="readout",
    )
    _run_until_success(
        _calibrate_drive_mixers,
        platform,
        controller,
        config,
        [0, 1],
        label="drive",
    )

    controller.disconnect()
