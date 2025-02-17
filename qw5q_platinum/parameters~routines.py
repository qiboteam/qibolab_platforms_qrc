{
    "nqubits": 5,
    "settings": {
        "nshots": 2048,
        "relaxation_time": 100000
    },
    "qubits": [
        0,
        1,
        2,
        3,
        4
    ],
    "topology": [
        [
            0,
            2
        ],
        [
            1,
            2
        ],
        [
            2,
            3
        ],
        [
            2,
            4
        ]
    ],
    "instruments": {
        "qm": {
            "bounds": {
                "waveforms": 40000,
                "readout": 30,
                "instructions": 1000000
            }
        },
        "twpa": {
            "power": 1.564,
            "frequency": 6531300000
        },
        "con1": {
            "2/o1": {
                "output_mode": "direct"
            },
            "2/o2": {
                "output_mode": "direct"
            },
            "1/o3": {
                "output_mode": "direct"
            },
            "1/o4": {
                "output_mode": "direct"
            },
            "1/o5": {
                "output_mode": "direct"
            },
            "1/o6": {
                "output_mode": "direct"
            },
            "1/o1": {
                "output_mode": "direct"
            },
            "1/o2": {
                "output_mode": "direct"
            },
            "1/o7": {
                "output_mode": "direct"
            },
            "1/o8": {
                "output_mode": "direct"
            },
            "2/o3": {
                "output_mode": "direct"
            },
            "2/o4": {
                "output_mode": "direct"
            },
            "4/o4": {
                "output_mode": "amplified"
            },
            "4/o1": {
                "output_mode": "amplified"
            },
            "4/o3": {
                "output_mode": "amplified"
            },
            "4/o2": {
                "filter": {
                    "feedforward": [
                        1.0891790415038731,
                        -1.024484298837039
                    ],
                    "feedback": [
                        0.935305257333166
                    ]
                },
                "output_mode": "amplified"
            },
            "4/o5": {
                "output_mode": "amplified"
            },
            "2/i1": {
                "gain": 10
            },
            "2/i2": {
                "gain": 10
            }
        },
        "octave1": {
            "o2": {
                "lo_frequency": 4900000000.0,
                "gain": -5
            },
            "o3": {
                "lo_frequency": 5100000000.0,
                "gain": -5
            },
            "o1": {
                "lo_frequency": 5650000000.0,
                "gain": -10
            },
            "o4": {
                "lo_frequency": 6600000000.0,
                "gain": -10
            }
        },
        "octave2": {
            "o1": {
                "lo_frequency": 7550000000,
                "gain": -5
            },
            "o2": {
                "lo_frequency": 6500000000.0,
                "gain": -5
            },
            "i1": {
                "lo_frequency": 7550000000
            }
        }
    },
    "native_gates": {
        "single_qubit": {
            "0": {
                "RX": {
                    "duration": 40, # Fixed
                    "amplitude": 0.16072838464175257, # Rabi + Flipping 
                    "shape": "Gaussian(5)",
                    "frequency": 4768143284, # Ramsey
                    "relative_start": 0,
                    "phase": 0,
                    "type": "qd"
                },
                "RX12": {
                    "duration": 40,
                    "amplitude": 0.18,
                    "shape": "Drag(5, 0.000)",
                    "frequency": 4482584846,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "MZ": {
                    "duration": 2000,
                    "amplitude": 0.00245, # Punchout
                    "shape": "Rectangular()",
                    "frequency": 7203205000, # Qubit Flux + Resonator Spectroscopy
                    "relative_start": 0,
                    "phase": 0,
                    "type": "ro"
                }
            },
            "1": {
                "RX": {
                    "duration": 40,
                    "amplitude": 0.08918772123861939,
                    "shape": "Gaussian(5)",
                    "frequency": 4813638753,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "RX12": {
                    "duration": 40,
                    "amplitude": 0.1,
                    "shape": "Drag(5, 0.000)",
                    "frequency": 0,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "MZ": {
                    "duration": 2000,
                    "amplitude": 0.00125,
                    "shape": "Rectangular()",
                    "frequency": 7336281962,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "ro"
                }
            },
            "2": {
                "RX": {
                    "duration": 40,
                    "amplitude": 0.15853787059834393,
                    "shape": "Gaussian(5)",
                    "frequency": 5518351609,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "RX12": {
                    "duration": 40,
                    "amplitude": 0.2,
                    "shape": "Drag(5, 0.000)",
                    "frequency": 5205873098,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "MZ": {
                    "duration": 2000,
                    "amplitude": 0.0012,
                    "shape": "Rectangular()",
                    "frequency": 7496260000,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "ro"
                }
            },
            "3": {
                "RX": {
                    "duration": 40,
                    "amplitude": 0.25531150748694875,
                    "shape": "Gaussian(5)",
                    "frequency": 6332114273,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "RX12": {
                    "duration": 40,
                    "amplitude": 0.2,
                    "shape": "Drag(5, 0.000)",
                    "frequency": 0,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "MZ": {
                    "duration": 2000,
                    "amplitude": 0.00165,
                    "shape": "Rectangular()",
                    "frequency": 7661092000,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "ro"
                }
            },
            "4": {
                "RX": {
                    "duration": 40,
                    "amplitude": 0.1415649807690657,
                    "shape": "Gaussian(5)",
                    "frequency": 6239342008,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "RX12": {
                    "duration": 40,
                    "amplitude": 0.3,
                    "shape": "Drag(5, 0.000)",
                    "frequency": 6236251170,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "qd"
                },
                "MZ": {
                    "duration": 2000,
                    "amplitude": 0.0023,
                    "shape": "Rectangular()",
                    "frequency": 7793902000,
                    "relative_start": 0,
                    "phase": 0.0,
                    "type": "ro"
                }
            }
        },
        "two_qubit": {
            "0-2": {
                "CZ": [
                    {
                        "duration": 29,
                        "amplitude": 0.2450118,
                        "shape": "Rectangular()",
                        "qubit": 3,
                        "relative_start": 0,
                        "type": "qf"
                    },
                    {
                        "type": "virtual_z",
                        "phase": -6.1387363925945575,
                        "qubit": 2
                    },
                    {
                        "type": "virtual_z",
                        "phase": -5.9194069237042095,
                        "qubit": 3
                    }
                ]
            },
            "1-2": {
                "CZ": [
                    {
                        "duration": 29,
                        "amplitude": 0.2450118,
                        "shape": "Rectangular()",
                        "qubit": 1,
                        "relative_start": 0,
                        "type": "qf"
                    },
                    {
                        "type": "virtual_z",
                        "phase": -6.1387363925945575,
                        "qubit": 2
                    },
                    {
                        "type": "virtual_z",
                        "phase": -5.9194069237042095,
                        "qubit": 1
                    }
                ]
            },
            "2-3": {
                "CZ": [
                    {
                        "duration": 29,
                        "amplitude": 0.23640401,
                        "shape": "Rectangular()",
                        "qubit": 3,
                        "relative_start": 0,
                        "type": "qf"
                    },
                    {
                        "type": "virtual_z",
                        "phase": -6.1387363925945575,
                        "qubit": 2
                    },
                    {
                        "type": "virtual_z",
                        "phase": -5.9194069237042095,
                        "qubit": 3
                    }
                ]
            },
            "2-4": {
                "CZ": [
                    {
                        "duration": 29,
                        "amplitude": 0.2450118,
                        "shape": "Rectangular()",
                        "qubit": 3,
                        "relative_start": 0,
                        "type": "qf"
                    },
                    {
                        "type": "virtual_z",
                        "phase": -6.1387363925945575,
                        "qubit": 2
                    },
                    {
                        "type": "virtual_z",
                        "phase": -5.9194069237042095,
                        "qubit": 3
                    }
                ]
            }
        }
    },
    "characterization": {
        "single_qubit": {
            "0": {
                "bare_resonator_frequency": 7199880000, # Resonator Spectroscopy (HP)
                "readout_frequency": 7203205000, # Qubit Flux + Resonator Spectroscopy
                "drive_frequency": 4768143284, # Qubit Spectroscopy + Ramsey 
                "anharmonicity": -286373266,
                "sweetspot": 0.36946520994429216,
                "asymmetry": 0.09002146499048984,
                "crosstalk_matrix": {
                    "0": 0.9758222890527934,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0
                },
                "Ec": 270000000,
                "Ej": 0.0,
                "g": 0.09002146499048984,
                "assignment_fidelity": 0.8718068744148724, # Single Shot
                "readout_fidelity": 0.7436137488297445, # Single Shot
                "gate_fidelity": 0.0,
                "effective_temperature": 0.0,
                "peak_voltage": 0,
                "pi_pulse_amplitude": 0.16072838464175257,
                "resonator_depletion_time": 0,
                "T1": 53438.82165776302,
                "T2": 21028, # Ramsey, T2
                "T2_spin_echo": 21217,
                "state0_voltage": 0,
                "state1_voltage": 0,
                "mean_gnd_states": [ # Single Shot
                    0.003377203424152313,
                    0.0015771929667372502
                ],
                "mean_exc_states": [ # Single Shot
                    0.005101026528971677,
                    0.001977514622064617
                ],
                "threshold": 0.0044455620738104015, # Single Shot
                "iq_angle": -0.22818433141114405, # Single Shot
                "mixer_drive_g": 0.0,
                "mixer_drive_phi": 0.0,
                "mixer_readout_g": 0.0,
                "mixer_readout_phi": 0.0
            },
            "1": {
                "bare_resonator_frequency": 7331800000,
                "readout_frequency": 7336281962,
                "drive_frequency": 4813638753,
                "anharmonicity": 292584018,
                "sweetspot": 0.42911850704082505,
                "asymmetry": 0.10632462221272213,
                "crosstalk_matrix": {
                    "0": 0,
                    "1": 0.8705873235798905,
                    "2": 0,
                    "3": 0,
                    "4": 0
                },
                "Ec": 270000000,
                "Ej": 0.0,
                "g": 0.10632462221272213,
                "assignment_fidelity": 0.8842501637197119,
                "readout_fidelity": 0.7685003274394238,
                "gate_fidelity": 0.0,
                "effective_temperature": 0.0,
                "peak_voltage": 0,
                "pi_pulse_amplitude": 0.08918772123861939,
                "resonator_depletion_time": 0,
                "T1": 41398.71780231028,
                "T2": 2603.383998096084,
                "T2_spin_echo": 0,
                "state0_voltage": 0,
                "state1_voltage": 0,
                "mean_gnd_states": [
                    -0.0007361571568675495,
                    -0.001881304447954196
                ],
                "mean_exc_states": [
                    -0.0004619412588283601,
                    -0.00470789641418373
                ],
                "threshold": 0.006137,
                "iq_angle": 1.395,
                "mixer_drive_g": 0.0,
                "mixer_drive_phi": 0.0,
                "mixer_readout_g": 0.0,
                "mixer_readout_phi": 0.0
            },
            "2": {
                "bare_resonator_frequency": 7490560000,
                "readout_frequency": 7496411943,
                "drive_frequency": 5518351609,
                "anharmonicity": -310651789,
                "sweetspot": 0.5547262771199553,
                "asymmetry": 0.10745777314995064,
                "crosstalk_matrix": {
                    "0": 0,
                    "1": 0,
                    "2": 0.8988244952677518,
                    "3": 0,
                    "4": 0
                },
                "Ec": 270000000,
                "Ej": 0.0,
                "g": 0.10745777314995064,
                "assignment_fidelity": 0.9754580714190183,
                "readout_fidelity": 0.9509161428380366,
                "gate_fidelity": 0.0,
                "effective_temperature": 0.0,
                "peak_voltage": 0,
                "pi_pulse_amplitude": 0.15853787059834393,
                "resonator_depletion_time": 2000,
                "T1": 28165.885336961088,
                "T2": 28165.885336961088,
                "T2_spin_echo": 0,
                "state0_voltage": 0,
                "state1_voltage": 0,
                "mean_gnd_states": [
                    -3.0402116409153694e-05,
                    -0.0030876930640144074
                ],
                "mean_exc_states": [
                    0.0031011093951441855,
                    -0.009096906458022554
                ],
                "threshold": 0.005648826583628785,
                "iq_angle": 1.090397105835069,
                "mixer_drive_g": 0.0,
                "mixer_drive_phi": 0.0,
                "mixer_readout_g": 0.0,
                "mixer_readout_phi": 0.0
            },
            "3": {
                "bare_resonator_frequency": 7658380000,
                "readout_frequency": 7661092000,
                "drive_frequency": 6332114273,
                "anharmonicity": 262310994,
                "sweetspot": 0.5926677,
                "asymmetry": 0.06005404789379201,
                "crosstalk_matrix": {
                    "0": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0.9999999999851821,
                    "4": 0
                },
                "Ec": 270000000,
                "Ej": 0.0,
                "g": 0.06062186761236172,
                "assignment_fidelity": 0.9572689581382907,
                "readout_fidelity": 0.9145379162765815,
                "gate_fidelity": 0.0,
                "effective_temperature": 0.0,
                "peak_voltage": 0,
                "pi_pulse_amplitude": 0.25531150748694875,
                "resonator_depletion_time": 0,
                "T1": 33828.69147881076,
                "T2": 1421.1187740901128,
                "T2_spin_echo": 24769,
                "state0_voltage": 0,
                "state1_voltage": 0,
                "mean_gnd_states": [
                    -0.0005905978761937221,
                    -0.0022180149502280732
                ],
                "mean_exc_states": [
                    0.0003805554022129899,
                    -0.004215724741840994
                ],
                "threshold": 0.002919770878315518,
                "iq_angle": 1.1183034795193743,
                "mixer_drive_g": 0.0,
                "mixer_drive_phi": 0.0,
                "mixer_readout_g": 0.0,
                "mixer_readout_phi": 0.0
            },
            "4": {
                "bare_resonator_frequency": 7791600000,
                "readout_frequency": 7793902000,
                "drive_frequency": 6239342008,
                "anharmonicity": 261390626,
                "sweetspot": -0.00028136270536068924,
                "asymmetry": 0.05988754921149063,
                "crosstalk_matrix": {
                    "0": 0,
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 1.0024398653468962
                },
                "Ec": 270000000,
                "Ej": 0.0,
                "g": 0.05988754921149063,
                "assignment_fidelity": 0.8807676875752306,
                "readout_fidelity": 0.7615353751504613,
                "gate_fidelity": 0.0,
                "effective_temperature": 0.0,
                "peak_voltage": 0,
                "pi_pulse_amplitude": 0.1415649807690657,
                "resonator_depletion_time": 0,
                "T1": 34231.46890053955,
                "T2": 1876.8095067556355,
                "T2_spin_echo": 0,
                "state0_voltage": 0,
                "state1_voltage": 0,
                "mean_gnd_states": [
                    -0.0011388063554582833,
                    0.00011226423674008162
                ],
                "mean_exc_states": [
                    -0.0024401254925049292,
                    -0.00090889545012815
                ],
                "threshold": 0.0017897843455987447,
                "iq_angle": 2.476243929935957,
                "mixer_drive_g": 0.0,
                "mixer_drive_phi": 0.0,
                "mixer_readout_g": 0.0,
                "mixer_readout_phi": 0.0
            }
        },
        "two_qubit": {
            "0-2": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "2-0": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "1-2": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "2-1": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "2-3": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "3-2": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "2-4": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            },
            "4-2": {
                "gate_fidelity": 0.0,
                "cz_fidelity": 0.0
            }
        }
    }
}