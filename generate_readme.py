import json
import os
import warnings
from typing import Union


def get_info(filename: str):

    with open(filename) as f:
        data = json.load(f)

    if not isinstance(data["topology"], list):
        raise RuntimeError(
            f"The topology is expected to be a list of edges (List[List[int, int]] or List[List[str, str]]), but received a {type(data['topology'])}."
        )

    info = {key: data[key] for key in ("nqubits", "qubits", "topology")}
    one_q_native_gates = list(
        next(iter(data["native_gates"]["single_qubit"].values())).keys()
    )
    two_q_native_gates = list(
        next(iter(data["native_gates"]["two_qubit"].values())).keys()
    )
    info.update(
        {
            "native_gates": {
                "single_qubit": one_q_native_gates,
                "two_qubit": two_q_native_gates,
            }
        }
    )
    return info


def create_mermaid_graph(
    nodes: Union[list[str], list[int]], topology: Union[list[str], list[int]]
):
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


def create_readme(filename: str):
    info = get_info(filename)
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

    platforms = [
        directory.name
        for directory in os.scandir(".")
        if directory.is_dir()
        and not (directory.name.startswith("_") or directory.name.startswith("."))
    ]

    for platform in platforms:

        filename = f"{platform}/parameters.json"
        try:
            readme_str = create_readme(filename)
        except FileNotFoundError:
            warnings.warn(
                f"Couldn't find ``{filename}``, unable to generate the README for platform ``{platform}``."
            )
            continue
        except RuntimeError as err:
            warnings.warn(
                err.args[0]
                + f" Unable to generate the README for platform ``{platform}``."
            )
            continue

        with open(f"{platform}/README.md", "w") as f:
            f.write(f"# {platform}\n")
            f.write(readme_str)
