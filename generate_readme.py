import json
import os
import sys
from typing import Union


def get_info(filename: str):

    with open(filename) as f:
        data = json.load(f)

    if not isinstance(data["topology"], list):
        raise TypeError

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
    node_indices = list(range(len(nodes)))
    edges = "\n    ".join([f"{edge[0]} <--> {edge[1]};" for edge in topology])
    markdown_str = f"""
```mermaid
graph TD;
    {edges}
```
"""
    return markdown_str


def create_readme(filename: str):
    info = get_info(filename)
    mermaid_graph = create_mermaid_graph(info["qubits"], info["topology"])
    readme_str = f"""
## Native Gates
**Single Qubit**: {", ".join(info["native_gates"]["single_qubit"])}

**Two Qubit**: {", ".join(info["native_gates"]["two_qubit"])}

## Topology
**Number of qubits**: {info["nqubits"]}

**Qubits**: {", ".join(info["qubits"])}
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
            continue
        except TypeError:
            continue

        with open(f"{platform}/README.md", "w") as f:
            f.write(f"# {platform}\n")
            f.write(readme_str)
