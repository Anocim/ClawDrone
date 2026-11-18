"""Measure the arrival rate of camera frames without depending on ROS."""

from collections import deque


class FrameStats:
    """Keep the arrival times of the latest frames and derive their rate."""

    def __init__(self, window=30):
        """Remember at most ``window`` arrival times (must be at least 2)."""
        if window < 2:
            raise ValueError('window must be at least 2')
        self._times = deque(maxlen=window)
        self.total = 0

    def add(self, stamp_sec):
        """Register a frame received at ``stamp_sec`` (monotonic seconds)."""
        self._times.append(float(stamp_sec))
        self.total += 1

    def rate_hz(self):
        """Return the mean frame rate over the window, or 0.0 if unknown."""
        if len(self._times) < 2:
            return 0.0
        span = self._times[-1] - self._times[0]
        if span <= 0.0:
            return 0.0
        return (len(self._times) - 1) / span
