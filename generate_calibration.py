import argparse
import json
from pathlib import Path



def single_qubits(o: dict) -> dict:
    return { q: {
            "resonator": {
                "bare_frequency": k["bare_resonator_frequency"],
                "dressed_frequency": k["readout_frequency"],
                },
            "qubit": {
                "frequency_01": k["drive_frequency"],
                "sweetspot": k["sweetspot"],
            },
            "readout":{
                "fidelity": k["readout_fidelity"],
                "ground_state": k["mean_gnd_states"],
                "excited_state": k["mean_exc_states"],
            },
            "t1": [k["T1"], None],
            "t2": [k["T2"], None],
            "t2_spin_echo": [k["T2_spin_echo"], None],
            "rb_fidelity": [k["gate_fidelity"], None],
    } for q, k in o.items()}


def two_qubits(o:dict) -> dict:
    return {qq :{
        "rb_fidelity": [k["gate_fidelity"], None],
        "cz_fidelity": [k["cz_fidelity"], None],
        } for qq, k in o.items()}


def upgrade(o: dict) -> dict:
    return {
        "single_qubits": single_qubits(o["characterization"]["single_qubit"]
        ),
        "two_qubits": two_qubits(o["characterization"]["two_qubit"]),
    }


def convert(path: Path):
    params = json.loads(path.read_text())
    new = upgrade(params)
    path.with_stem("calibration_new").write_text(json.dumps(new, indent=4))


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*", type=Path)
    return parser.parse_args()


def main():
    args = parse()

    for p in args.path:
        convert(p)


if __name__ == "__main__":
    main()
