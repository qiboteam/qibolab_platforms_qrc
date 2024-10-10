import pathlib

import pytest
from qibolab import Platform, create_platform

PATH = pathlib.Path(__file__).parents[1]


def idfn(path):
    """Helper function to identify platform tested."""
    try:
        return str(path.parent).split("/")[-1]
    except AttributeError:
        return None


@pytest.mark.parametrize("path", PATH.glob("*/platform.py"), ids=idfn)
def test_create(path):
    """Test that platform can be created."""
    platform = create_platform(path.parent)
    qubit = next(iter(platform.qubits))
    rx_sequence = platform.natives.single_qubit[qubit].RX()
    mz_sequence = platform.natives.single_qubit[qubit].MZ()
    assert isinstance(platform, Platform)
