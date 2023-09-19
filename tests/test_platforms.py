import os
import pathlib

import pytest
from qibolab import Platform, create_platform

PATH = pathlib.Path(__file__).parents[1]


@pytest.mark.parametrize("path", PATH.glob("*.py"))
def test_create(path):
    """Test that platform can be created."""
    platform = create_platform(path.stem)
    qubit = next(iter(platform.qubits))
    rx_pulse = platform.create_RX_pulse(qubit)
    mz_pulse = platform.create_MZ_pulse(qubit, start=rx_pulse.duration)
    assert isinstance(platform, Platform)
