import argparse
import ast
import json
from pathlib import Path

from pydantic import TypeAdapter
from qibolab._core.serialize import NdArray

NONSERIAL = lambda: None
"""Raise an error if survives in the final object to be serialized."""


def channel_config(o: dict) -> dict:
    return {}


def configs(
    instruments: dict, single: dict, couplers: dict, characterization: dict
) -> dict:
    return (
        {
            f"{k}/bounds": (v["bounds"] | {"kind": "bounds"})
            for k, v in instruments.items()
            if "bounds" in v
        }
        | {
            k: (v | {"kind": "oscillator"})
            for k, v in instruments.items()
            if "twpa" in k
        }
        | {
            channel(id, pulse["type"]): channel_config(pulse)
            for id, gates in single.items()
            for gate, pulse in gates.items()
        }
        | {
            channel(id, "ro"): {
                "kind": "acquisition",
                "delay": 0.0,
                "smearing": 0.0,
                "threshold": char["threshold"],
                "iq_angle": char["iq_angle"],
                "kernel": None,
            }
            for id, char in characterization["single_qubit"].items()
        }
        | {
            channel(id, "qf"): {"kind": "dc", "offset": char["sweetspot"]}
            for id, char in characterization["single_qubit"].items()
        }
        | {
            channel(id, "coupler"): {"kind": "dc", "offset": char["sweetspot"]}
            for id, char in characterization.get("coupler", {}).items()
        }
    )


def channel(qubit: str, type_: str) -> str:
    kind = (
        "flux"
        if type_ == "qf" or type_ == "coupler"
        else "acquisition"
        if type_ == "ro"
        else "drive"
    )
    element = qubit if type_ != "coupler" else f"coupler_{qubit}"
    return f"{element}/{kind}"


SHAPES = {
    "rectangular": {},
    "gaussian": {"rel_sigma": lambda s: 1 / s},
    "drag": {"rel_sigma": lambda s: 1 / s, "beta": lambda s: s},
    "custom": {"i_": lambda s: TypeAdapter(NdArray).dump_json(s).decode()},
}


def envelope(o: str) -> dict:
    expr = ast.parse(o).body[0]
    assert isinstance(expr, ast.Expr)
    call = expr.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    kind = call.func.id.lower()
    kwargs = {}
    shape = SHAPES[kind]
    for arg, spec in zip(call.args, shape.items()):
        kwargs[spec[0]] = spec[1](ast.literal_eval(arg))
    for arg in call.keywords:
        assert isinstance(arg.value, ast.Constant)
        kwargs[arg.arg] = ast.literal_eval(arg.value)
    return {"kind": kind, **kwargs}


def pulse(o: dict) -> dict:
    return {
        "kind": "pulse",
        "duration": o["duration"],
        "amplitude": o["amplitude"],
        "envelope": envelope(o["shape"]),
        "relative_phase": o.get("phase"),
    }


def acquisition(o: dict) -> dict:
    return {
        "kind": "readout",
        "acquisition": {"kind": "acquisition", "duration": o["duration"]},
        "probe": pulse(o),
    }


def virtualz(o: dict) -> dict:
    return {"kind": "virtualz", "phase": o["phase"]}


def pulse_like(o: dict) -> dict:
    return (
        acquisition(o)
        if o["type"] == "ro"
        else virtualz(o)
        if o["type"] == "virtual_z"
        else pulse(o)
    )


def single_pulse(o: dict) -> dict:
    return {
        id: {
            gid: [(channel(id, gate["type"]), pulse_like(gate))]
            for gid, gate in gates.items()
        }
        for id, gates in o.items()
    }


def two_qubit(o: dict) -> dict:
    return {
        id: {
            gid: [
                (
                    channel(
                        pulse.get("qubit", pulse.get("coupler", NONSERIAL)),
                        pulse["type"],
                    ),
                    pulse_like(pulse),
                )
                for pulse in gate
            ]
            for gid, gate in gates.items()
        }
        for id, gates in o.items()
    }


def natives(o: dict) -> dict:
    return {
        "single_qubit": single_pulse(o["single_qubit"]),
        "coupler": {
            f"coupler_{k}": v for k, v in single_pulse(o.get("coupler", {})).items()
        },
        "two_qubit": two_qubit(o["two_qubit"]),
    }


def upgrade(o: dict) -> dict:
    return {
        "settings": o["settings"],
        "configs": configs(
            o["instruments"],
            o["native_gates"]["single_qubit"],
            o["native_gates"].get("coupler", {}),
            o["characterization"],
        ),
        "native_gates": natives(o["native_gates"]),
    }


def convert(path: Path):
    params = json.loads(path.read_text())
    new = upgrade(params)
    path.with_stem(path.stem + "-new").write_text(json.dumps(new, indent=4))


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
