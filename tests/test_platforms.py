import os
import pathlib

import pytest
from qibolab import Platform, create_platform

PATH = pathlib.Path(__file__).parent.parent


def platform_names():
    """Yield the names of all platforms in the repository."""
    for filename in os.listdir(PATH):
        split = filename.split(".")
        if split[-1] == "py":
            yield split[0]


@pytest.mark.parametrize("name", platform_names())
def test_create(name):
    """Test that platform ``name`` can be created."""
    platform = create_platform(name)
    qubit = next(iter(platform.qubits))
    rx_pulse = platform.create_RX_pulse(qubit)
    mz_pulse = platform.create_MZ_pulse(qubit, start=rx_pulse.duration)
    assert isinstance(platform, Platform)
