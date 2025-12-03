"""Small script that automatically parses some basic information from the `parameters.json` file and organizes it in a `README.md`"""

import argparse
import json
from pathlib import Path
from typing import Union


def get_info(parameters_path: Path, calibration_path: Path) -> dict:
    """Open ``filename`` and extracts: `nqubits`, `qubits`, `topology` and `native_gates`."""

    with open(parameters_path) as f:
        parameters_data = json.load(f)

    with open(calibration_path) as f:
        calibration_data = json.load(f)

    qubits = list(calibration_data['single_qubits'].keys())
    topology = [s.split('-') for s in calibration_data['two_qubits'].keys()]
    info = {"nqubits": len(qubits), "qubits": qubits, "topology": topology}

    # Do we want the union or intersection of gates for the various qubits?
    single_q_native_gates = set()
    for gate_dict in parameters_data['native_gates']['single_qubit'].values():
        for gate, val in gate_dict.items():
            if val is not None:
                single_q_native_gates.add(gate)

    two_q_native_gates = set()
    for gate_dict in parameters_data['native_gates']['two_qubit'].values():
        for gate, val in gate_dict.items():
            if val is not None:
                two_q_native_gates.add(gate)

    info.update(
        {
            "native_gates": {
                "single_qubit": single_q_native_gates,
                "two_qubit": two_q_native_gates,
            }
        }
    )
    return info


def create_mermaid_graph(
    nodes: Union[list[str], list[int]],
    topology: Union[list[list[str]], list[list[int]]],
) -> str:
    """Create a markdown string encoding a mermaid graph given by the input `nodes` and `topology`."""
    node_to_index = dict(zip(nodes, range(len(nodes))))
    if isinstance(nodes[0], int) or nodes[0].isdecimal():
        edges = "\n    ".join(
            [
                f"{edge[0]}(({str(edge[0])})) <--> {edge[1]}(({str(edge[1])}));"
                for edge in topology
            ]
        )
    else:
        edges = "\n    ".join(
            [
                f"{node_to_index[edge[0]]}(({edge[0]})) <--> {node_to_index[edge[1]]}(({edge[1]}));"
                for edge in topology
            ]
        )
    markdown_str = f"""
```mermaid
---
config:
layout: elk
---
graph TD;
    {edges}
```
"""
    return markdown_str


def create_readme(info: dict) -> str:
    """Build the `README.md` for the input `filename`."""
    mermaid_graph = create_mermaid_graph(info["qubits"], info["topology"])
    qubits = (
        ", ".join([str(q) for q in info["qubits"]])
        if isinstance(info["qubits"][0], int) or info["qubits"][0].isdecimal()
        else ", ".join([f"{q} ({i})" for i, q in enumerate(info["qubits"])])
    )
    readme_str = f"""
## Native Gates
**Single Qubit**: {", ".join(info["native_gates"]["single_qubit"])}

**Two Qubit**: {", ".join(info["native_gates"]["two_qubit"])}

## Topology
**Number of qubits**: {info["nqubits"]}

**Qubits**: {qubits}
{mermaid_graph}
"""
    return readme_str


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="generate_readme",
        description="Automatically generate the README.md for the given input platform/s.",
    )
    parser.add_argument("platform", nargs="+", type=Path)
    platforms = parser.parse_args().platform

    for platform in platforms:
        parameters_file = platform / "parameters.json"
        calibration_file = platform / "calibration.json"
        info = get_info(parameters_file, calibration_file)
        readme_str = create_readme(info)
        (platform / "README.md").write_text(f"# {platform}\n{readme_str}")
