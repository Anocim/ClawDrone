"""Exercise telemetry evaluation without ROS or a simulator."""

from dataclasses import replace
import math

import pytest

from f550_monitor.telemetry import (
    ERROR, OK, STALE, WARN, MonitorConfig, TelemetryMonitor, TelemetrySample,
)


@pytest.fixture
def monitor():
    """Provide a controllable monotonic clock without sleeping."""
    now = [100.0]
    return TelemetryMonitor(MonitorConfig(), clock=lambda: now[0]), now


@pytest.fixture
def sample():
    """Provide finite, normalized NED odometry."""
    return TelemetrySample((1.0, 2.0, -3.0), (1.0, 2.0, 2.0),
                           (1.0, 0.0, 0.0, 0.0), 1, 1)


def test_valid_telemetry(monitor, sample):
    """Interpret altitude as negative down and calculate Euclidean speed."""
    evaluator, _ = monitor
    evaluator.receive(sample)
    result = evaluator.evaluate()
    assert result.level == OK
    assert float(result.values['local_altitude_m']) == 3.0
    assert float(result.values['speed_mps']) == 3.0
    assert float(result.values['position_north_m']) == 1.0


def test_missing_telemetry(monitor):
    """Distinguish the initial wait from communication loss."""
    evaluator, now = monitor
    assert evaluator.evaluate().level == WARN
    assert 'Waiting' in evaluator.evaluate().message
    now[0] += 2.01
    assert evaluator.evaluate().level == STALE
    assert 'Missing' in evaluator.evaluate().message


def test_timeout_and_recovery(monitor, sample):
    """Use receipt time and recover after fresh telemetry arrives."""
    evaluator, now = monitor
    evaluator.receive(sample)
    now[0] += 2.0
    assert evaluator.evaluate().level == OK
    now[0] += 0.01
    assert evaluator.evaluate().level == STALE
    evaluator.receive(sample)
    assert evaluator.evaluate().level == OK


@pytest.mark.parametrize('field,length', [
    ('position', 3), ('velocity', 3), ('quaternion', 4),
])
@pytest.mark.parametrize('bad', [math.nan, math.inf, -math.inf])
def test_non_finite_values(monitor, sample, field, length, bad):
    """Reject invalid values in every monitored vector."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, **{field: (bad,) + (0.0,) * (length - 1)}))
    assert evaluator.evaluate().level == ERROR
    assert f'Invalid {field}' in evaluator.evaluate().message


@pytest.mark.parametrize('quaternion', [(0.0,) * 4, (2.0, 0.0, 0.0, 0.0), (1.0,)])
def test_invalid_quaternion(monitor, sample, quaternion):
    """Reject zero, unnormalized and malformed quaternions."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, quaternion=quaternion))
    assert evaluator.evaluate().level == ERROR


def test_altitude_threshold(monitor, sample):
    """Warn on local height above the configured maximum."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, position=(0.0, 0.0, -10.1)))
    result = evaluator.evaluate()
    assert result.level == WARN
    assert 'altitude exceeds' in result.message


def test_speed_threshold(monitor, sample):
    """Warn on speed magnitude, including downward velocity."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, velocity=(0.0, 0.0, -5.1)))
    result = evaluator.evaluate()
    assert result.level == WARN
    assert 'Speed exceeds' in result.message


def test_threshold_boundaries_and_ned_sign(monitor, sample):
    """Allow exact limits and retain signed altitude below the origin."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, position=(0.0, 0.0, -10.0),
                              velocity=(3.0, 4.0, 0.0)))
    assert evaluator.evaluate().level == OK
    evaluator.receive(replace(sample, position=(0.0, 0.0, 20.0)))
    assert evaluator.evaluate().level == OK
    assert float(evaluator.evaluate().values['local_altitude_m']) == -20.0


@pytest.mark.parametrize('frame', [0, 2, 3, 255])
def test_pose_frame(monitor, sample, frame):
    """Do not label unsupported position frames as NED or infer altitude."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, pose_frame=frame))
    result = evaluator.evaluate()
    assert result.level == WARN
    assert 'local_altitude_m' not in result.values
    assert 'position_north_m' not in result.values
    assert 'speed_mps' in result.values


@pytest.mark.parametrize('frame', [0, 2, 3, 255])
def test_velocity_frame(monitor, sample, frame):
    """Keep body and FRD velocities separate from NED interpretation."""
    evaluator, _ = monitor
    evaluator.receive(replace(sample, velocity_frame=frame))
    result = evaluator.evaluate()
    assert result.level == WARN
    assert 'speed_mps' not in result.values
    assert 'velocity_north_mps' not in result.values
    assert 'local_altitude_m' in result.values


def test_error_and_stale_precedence(monitor, sample):
    """Preserve invalid-value details when receipt subsequently times out."""
    evaluator, now = monitor
    evaluator.receive(replace(sample, position=(math.nan, 0.0, 0.0), velocity_frame=3))
    assert evaluator.evaluate().level == ERROR
    now[0] += 3.0
    result = evaluator.evaluate()
    assert result.level == STALE
    assert 'Invalid position' in result.message
    assert 'Unsupported velocity' in result.message


@pytest.mark.parametrize('field', list(vars(MonitorConfig())))
@pytest.mark.parametrize('value', [0.0, -1.0, math.nan, math.inf])
def test_invalid_configuration(field, value):
    """Fail fast for non-finite or non-positive limits."""
    with pytest.raises(ValueError):
        MonitorConfig(**{field: value})


def test_custom_configuration(sample):
    """Honor custom limits and quaternion tolerance."""
    evaluator = TelemetryMonitor(MonitorConfig(0.5, 2.0, 2.0, 0.05))
    evaluator.receive(replace(sample, quaternion=(1.02, 0.0, 0.0, 0.0)))
    result = evaluator.evaluate()
    assert result.level == WARN
    assert 'altitude exceeds' in result.message
    assert 'Speed exceeds' in result.message
    with pytest.raises(ValueError):
        MonitorConfig(quaternion_norm_tolerance=1.0)
