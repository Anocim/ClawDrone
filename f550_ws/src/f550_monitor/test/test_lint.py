"""Run the ROS Python style checks when invoked through colcon."""

from pathlib import Path

from ament_flake8.main import main_with_errors
from ament_pep257.main import main as pep257_main
import pytest


@pytest.mark.linter
def test_flake8():
    """Check Python style throughout this package."""
    result, errors = main_with_errors(argv=[str(Path(__file__).parents[1])])
    assert result == 0, '\n'.join(errors)


@pytest.mark.linter
def test_pep257():
    """Check Python docstrings throughout this package."""
    assert pep257_main(argv=[str(Path(__file__).parents[1])]) == 0
