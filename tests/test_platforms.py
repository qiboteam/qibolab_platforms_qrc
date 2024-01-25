import pathlib
import pytest
from qibolab import Platform, create_platform

PATH = pathlib.Path(__file__).parents[1]


@pytest.mark.parametrize("path", PATH.glob('**/platform.py'))
def test_create(path):
    """Test that platform can be created."""
    print(path.parent)
    platform = create_platform(path.parent)
    qubit = next(iter(platform.qubits))
    rx_pulse = platform.create_RX_pulse(qubit)
    _ = platform.create_MZ_pulse(qubit, start=rx_pulse.duration)
    assert isinstance(platform, Platform)
