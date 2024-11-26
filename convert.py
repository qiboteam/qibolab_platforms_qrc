"""Converts parameters.json to parameters.json and calibration.json
"""

import argparse
import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pydantic import TypeAdapter
from qibolab._core.serialize import NdArray

NONSERIAL = lambda: None
"""Raise an error if survives in the final object to be serialized."""
QM_TIME_OF_FLIGHT = 224
"""Default time of flight for QM platforms (in 0.1 this was hard-coded in platform.py)."""


def channel_from_pulse(pulse: dict) -> dict:
    return {"kind": "iq", "frequency": pulse["frequency"]}


@dataclass
class QmConnection:
    instrument: str
    port: str
    output_mode: str = "triggered"


def qm_configs(conf: dict, instruments: dict, instrument_channels: dict) -> dict:
    for channel, conn in instrument_channels.items():
        connection = QmConnection(**conn)
        settings = instruments.get(connection.instrument, {}).get(connection.port, {})
        if channel in conf:
            kind = conf[channel]["kind"]
            if kind == "acquisition":
                conf[channel].update(
                    {
                        "kind": "qm-acquisition",
                        "delay": QM_TIME_OF_FLIGHT,
                        "gain": settings.get("gain", 0),
                    }
                )
            elif kind == "dc":
                conf[channel].update(
                    {
                        "kind": "opx-output",
                        "filter": settings.get("filter", {}),
                        "output_mode": settings.get("output_mode", "direct"),
                    }
                )
            else:
                raise NotImplementedError
        else:
            conf[channel] = {
                "kind": "octave-oscillator",
                "frequency": settings["lo_frequency"],
                "power": settings["gain"],
                "output_mode": connection.output_mode,
            }
    return conf


def configs(
    instruments: dict,
    single: dict,
    couplers: dict,
    characterization: dict,
    connections: Optional[dict] = None,
) -> dict:
    conf = (
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
            channel(id, pulse["type"], gate=gate): channel_from_pulse(pulse)
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
    if connections is not None:
        if connections["kind"] == "qm":
            conf = qm_configs(conf, instruments, connections["channels"])
        else:
            raise NotImplementedError
    return conf


def channel(qubit: str, type_: str, gate: Optional[str] = None) -> str:
    kind = (
        "flux"
        if type_ == "qf" or type_ == "coupler"
        else (
            "probe"
            if gate == "MZ"
            else (
                "acquisition"
                if type_ == "ro"
                else "drive12" if gate == "RX12" else "drive"
            )
        )
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


def pulse(o: dict, rescale: float) -> dict:
    return {
        "kind": "pulse",
        "duration": o["duration"],
        "amplitude": rescale * o["amplitude"],
        "envelope": envelope(o["shape"]),
        "relative_phase": o.get("phase", 0.0),
    }


def acquisition(o: dict, rescale: float) -> dict:
    return {
        "kind": "readout",
        "acquisition": {"kind": "acquisition", "duration": o["duration"]},
        "probe": pulse(o, rescale),
    }


def virtualz(o: dict) -> dict:
    return {"kind": "virtualz", "phase": o["phase"]}


def pulse_like(o: dict, rescale: float) -> dict:
    return (
        acquisition(o, rescale)
        if o["type"] == "ro"
        else virtualz(o) if o["type"] == "virtual_z" else pulse(o, rescale)
    )


def single_pulse(o: dict, rescale: float) -> dict:
    return {
        id: {
            gid: [(channel(id, gate["type"]), pulse_like(gate, rescale))]
            for gid, gate in gates.items()
        }
        for id, gates in o.items()
    }


def two_qubit(o: dict, rescale: float) -> dict:
    return {
        id: {
            gid: [
                (
                    channel(
                        pulse.get("qubit", pulse.get("coupler", NONSERIAL)),
                        pulse["type"],
                    ),
                    pulse_like(pulse, rescale),
                )
                for pulse in gate
            ]
            for gid, gate in gates.items()
        }
        for id, gates in o.items()
    }


def natives(o: dict, rescale: float) -> dict:
    return {
        "single_qubit": single_pulse(o["single_qubit"], rescale),
        "coupler": {
            f"coupler_{k}": v
            for k, v in single_pulse(o.get("coupler", {}), rescale).items()
        },
        "two_qubit": two_qubit(o["two_qubit"], rescale),
    }


def upgrade(o: dict, connections: Optional[dict] = None) -> dict:
    rescale = 2 if connections is not None and connections["kind"] == "qm" else 1
    return {
        "settings": o["settings"],
        "configs": configs(
            o["instruments"],
            o["native_gates"]["single_qubit"],
            o["native_gates"].get("coupler", {}),
            o["characterization"],
            connections,
        ),
        "native_gates": natives(o["native_gates"], rescale),
    }


def single_qubits_cal(o: dict) -> dict:
    return {
        q: {
            "resonator": {
                "bare_frequency": k["bare_resonator_frequency"],
                "dressed_frequency": k["readout_frequency"],
            },
            "qubit": {
                "frequency_01": k["drive_frequency"],
                "sweetspot": k["sweetspot"],
            },
            "readout": {
                "fidelity": k["readout_fidelity"],
                "ground_state": k["mean_gnd_states"],
                "excited_state": k["mean_exc_states"],
            },
            "t1": [k["T1"], None],
            "t2": [k["T2"], None],
            "t2_spin_echo": [k["T2_spin_echo"], None],
            "rb_fidelity": [k["gate_fidelity"], None],
        }
        for q, k in o.items()
    }


def two_qubits_cal(o: dict) -> dict:
    return {
        qq: {
            "rb_fidelity": [k["gate_fidelity"], None],
            "cz_fidelity": [k["cz_fidelity"], None],
        }
        for qq, k in o.items()
    }


def upgrade_cal(o: dict) -> dict:
    return {
        "single_qubits": single_qubits_cal(o["characterization"]["single_qubit"]),
        "two_qubits": two_qubits_cal(o["characterization"]["two_qubit"]),
    }


def convert(path: Path, connections_path: Optional[Path] = None):
    params = json.loads(path.read_text())
    connections = (
        json.loads(connections_path.read_text())
        if connections_path is not None
        else None
    )
    new = upgrade(params, connections)
    cal = upgrade_cal(params)
    path.with_stem(path.stem + "-new").write_text(json.dumps(new, indent=4))
    path.with_stem("calibration").write_text(json.dumps(cal, indent=4))


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="*", type=Path)
    parser.add_argument("--connections", nargs="*", default=None, type=Path)
    return parser.parse_args()


def main():
    args = parse()
    connections = args.connections
    if connections is not None:
        assert len(args.path) == len(connections)
    else:
        connections = len(args.path) * [None]

    for p, c in zip(args.path, connections):
        convert(p, c)


if __name__ == "__main__":
    main()
