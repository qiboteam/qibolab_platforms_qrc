# qpu169

## Native Gates
**Single Qubit**: MZ, RX, RX90

**Two Qubit**: CNOT

## Topology
**Number of qubits**: 4

**Qubits**: 0, 1, 2, 3

```mermaid
---
config:
layout: elk
---
graph TD;
    0((0)) <--> 1((1));
    1((1)) <--> 2((2));
    2((2)) <--> 3((3));
```


## Qubit fidelity and coherence times

| Qubit | Assignment Fidelity | T1 (µs) | T2 (µs) | Gate infidelity (e-3) |
| --- | --- | --- | --- | --- |
| 0 | 0.95 | 24.2 ± 2.3 | 24.7 ± 4.8 | 4.3 ± 0.59 |
| 1 | 0.95 | 16.5 ± 3.1 | 20.2 ± 6.0 | 2.3 ± 1.2 |
| 2 | 0.97 | 12.3 ± 1.7 | 11.7 ± 1.8 | 2.4 ± 0.28 |
| 3 | 0.95 | 2.2 ± 0.1 | 3.4 ± 0.3 | 12 ± 0.47 |
