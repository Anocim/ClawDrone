"""Evaluate PX4 odometry without ROS dependencies or control side effects."""

from dataclasses import dataclass
import math
import time
from typing import Callable, Dict, Optional, Tuple


# Match diagnostic_msgs/DiagnosticStatus and the vendored VehicleOdometry enums.
OK, WARN, ERROR, STALE = 0, 1, 2, 3
NED = 1


@dataclass(frozen=True)
class MonitorConfig:
    """Startup configuration; limits are preliminary simulation warnings."""

    telemetry_timeout_sec: float = 2.0
    altitude_warning_m: float = 10.0
    speed_warning_mps: float = 5.0
    quaternion_norm_tolerance: float = 0.01

    def __post_init__(self):
        """Reject unusable limits before monitoring starts."""
        for name, value in vars(self).items():
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f'{name} must be finite and greater than zero')
        if self.quaternion_norm_tolerance >= 1.0:
            raise ValueError('quaternion_norm_tolerance must be less than one')


@dataclass(frozen=True)
class TelemetrySample:
    """Relevant VehicleOdometry fields; quaternion order is (w, x, y, z)."""

    position: Tuple[float, ...]
    velocity: Tuple[float, ...]
    quaternion: Tuple[float, ...]
    pose_frame: int
    velocity_frame: int


@dataclass(frozen=True)
class Evaluation:
    """ROS-independent diagnostic result."""

    level: int
    message: str
    values: Dict[str, str]


class TelemetryMonitor:
    """Track receipt age using an injectable monotonic clock."""

    def __init__(
        self, config: MonitorConfig,
        clock: Callable[[], float] = time.monotonic,
    ):
        """Initialize the wait interval and immutable sample storage."""
        self.config = config
        self._clock = clock
        self._started = clock()
        self._received: Optional[float] = None
        self._sample: Optional[TelemetrySample] = None

    def receive(self, sample: TelemetrySample):
        """Record receipt, including invalid samples, without masking errors."""
        self._sample = sample
        self._received = self._clock()

    def evaluate(self) -> Evaluation:
        """Return current health; unsupported frames are never treated as NED."""
        now = self._clock()
        values = {name: str(value) for name, value in vars(self.config).items()}
        if self._sample is None:
            age = now - self._started
            values['waiting_sec'] = str(age)
            if age > self.config.telemetry_timeout_sec:
                return Evaluation(STALE, 'Missing telemetry: no samples received', values)
            return Evaluation(WARN, 'Waiting for initial telemetry', values)

        age = now - self._received
        sample = self._sample
        values.update({
            'receipt_age_sec': str(age),
            'pose_frame': str(sample.pose_frame),
            'velocity_frame': str(sample.velocity_frame),
            'position_raw_m': str(sample.position),
            'velocity_raw_mps': str(sample.velocity),
            'quaternion_wxyz': str(sample.quaternion),
        })
        errors = []
        warnings = []

        def valid_vector(name, vector, length):
            if len(vector) != length or not all(math.isfinite(x) for x in vector):
                errors.append(f'Invalid {name}: expected {length} finite values')
                return False
            return True

        position_valid = valid_vector('position', sample.position, 3)
        velocity_valid = valid_vector('velocity', sample.velocity, 3)
        if valid_vector('quaternion', sample.quaternion, 4):
            norm = math.hypot(*sample.quaternion)
            values['quaternion_norm'] = str(norm)
            if not math.isfinite(norm) or abs(norm - 1.0) > (
                self.config.quaternion_norm_tolerance
            ):
                errors.append('Invalid quaternion: norm must be near one')

        if sample.pose_frame != NED:
            warnings.append('Unsupported pose frame; NED position/altitude unavailable')
        elif position_valid:
            for axis, value in zip(('north', 'east', 'down'), sample.position):
                values[f'position_{axis}_m'] = str(value)
            altitude = -sample.position[2]
            values['local_altitude_m'] = str(altitude)
            if altitude > self.config.altitude_warning_m:
                warnings.append('Local altitude exceeds simulation warning threshold')

        if sample.velocity_frame != NED:
            warnings.append('Unsupported velocity frame; NED velocity/speed unavailable')
        elif velocity_valid:
            for axis, value in zip(('north', 'east', 'down'), sample.velocity):
                values[f'velocity_{axis}_mps'] = str(value)
            speed = math.hypot(*sample.velocity)
            values['speed_mps'] = str(speed)
            if not math.isfinite(speed):
                errors.append('Invalid speed: magnitude is non-finite')
            elif speed > self.config.speed_warning_mps:
                warnings.append('Speed exceeds simulation warning threshold')

        issues = errors + warnings
        if age > self.config.telemetry_timeout_sec:
            return Evaluation(
                STALE, '; '.join(['Stale telemetry: receipt timeout'] + issues), values,
            )
        level = ERROR if errors else WARN if warnings else OK
        return Evaluation(level, '; '.join(issues) or 'Normal operation', values)
