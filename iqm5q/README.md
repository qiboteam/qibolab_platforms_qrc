# iqm5q

## Native Gates
**Single Qubit**: RX, MZ

**Two Qubit**: 

## Topology
**Number of qubits**: 5

**Qubits**: 0, 1, 2, 3, 4

```mermaid
---
config:
layout: elk
---
graph TD;
    0((0)) <--> 2((2));
    1((1)) <--> 2((2));
    2((2)) <--> 3((3));
    2((2)) <--> 4((4));
```


## Qubit fidelity and coherence times

| Qubit | Assignment Fidelity | T1 (µs) | T2 (µs) | Gate infidelity (e-3) |
| --- | --- | --- | --- | --- |
| 0 | 0.95 | 23.1 | 10.7 | 0.0 |
| 1 | 0.89 | 18.4 | 11.5 | 0.0 |
| 2 | 0.94 | 8.5 | 3.6 | 0.0 |
| 3 | 0.94 | 24.0 | 3.3 | 0.0 |
| 4 | 0.93 | 7.0 | 9.6 | 0.0 |

