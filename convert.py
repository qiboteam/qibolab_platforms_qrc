import argparse
import json
import re
from pathlib import Path


def configs() -> dict:
    return {}


def channel(qubit: str, gate: str):
    kind = (
        "drive" if gate.startswith("RX") else "acquisition" if gate == "MZ" else "flux"
    )
    return f"{qubit}/{kind}"


SHAPES = {"rectangular": {}, "gaussian": {"rel_sigma": lambda s: 1 / float(s)}}
SHAPE = re.compile(r"(?P<kind>[a-zA-Z_]\w*)\((?P<args>.*)\)")
ARG = re.compile(r"(?:(?P<name>\w+)=)?(?P<value>.*)")


def envelope(o: str) -> dict:
    shape = SHAPE.match(o)
    assert shape is not None
    kind = shape["kind"].lower()
    kwargs = {}
    for param, spec in zip(shape["args"].split(","), SHAPES[kind].items()):
        arg = ARG.match(param)
        assert arg is not None
        try:
            name = arg["name"]
        except KeyError:
            name = spec[0]
        kwargs[name] = spec[1](arg["value"])
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


def pulse_like(o: dict) -> dict:
    return acquisition(o) if o["type"] == "ro" else pulse(o)


def single_pulse(o: dict) -> dict:
    return {
        id: {gid: [(channel(id, gid), pulse_like(gate))] for gid, gate in gates.items()}
        for id, gates in o.items()
    }


def natives(o: dict) -> dict:
    return {
        "single_qubit": single_pulse(o["single_qubit"]),
        "coupler": single_pulse(o["coupler"]),
        "two_qubit": {},
    }


def upgrade(o: dict) -> dict:
    return {
        "settings": o["settings"],
        "configs": configs(),
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
