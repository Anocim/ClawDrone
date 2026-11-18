"""Unit tests for the ROS-independent frame rate helper."""

import pytest

from f550_vision.frame_stats import FrameStats


def test_rate_is_zero_without_enough_frames():
    """Zero or one frame cannot define a rate."""
    stats = FrameStats()
    assert stats.rate_hz() == 0.0
    stats.add(1.0)
    assert stats.rate_hz() == 0.0


def test_rate_matches_regular_arrivals():
    """Ten frames spaced 0.1 s apart are 10 Hz."""
    stats = FrameStats()
    for index in range(10):
        stats.add(index * 0.1)
    assert stats.rate_hz() == pytest.approx(10.0)
    assert stats.total == 10


def test_window_forgets_old_frames():
    """Only the latest frames count towards the rate."""
    stats = FrameStats(window=3)
    for stamp in (0.0, 10.0, 10.5, 11.0):
        stats.add(stamp)
    assert stats.rate_hz() == pytest.approx(2.0)


def test_identical_stamps_do_not_divide_by_zero():
    """Frames sharing a timestamp give an unknown rate."""
    stats = FrameStats()
    stats.add(1.0)
    stats.add(1.0)
    assert stats.rate_hz() == 0.0


def test_window_must_allow_a_rate():
    """A window below two frames is rejected."""
    with pytest.raises(ValueError):
        FrameStats(window=1)
