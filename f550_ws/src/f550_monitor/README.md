# f550_monitor

Read-only telemetry monitoring for ClawDrone's F550 using ROS 2 Humble,
Python 3 and `ament_python`. `telemetry.py` evaluates snapshots without ROS;
`telemetry_monitor_node.py` handles subscription and diagnostic publication.
It never arms, changes modes, or publishes PX4 commands or emergency overrides.
Existing `f550_control` and `px4_msgs` packages are independent and unchanged.

## Topics and dependencies

| Direction | Topic | Type |
| --- | --- | --- |
| Subscribe | `/fmu/out/vehicle_odometry` | `px4_msgs/msg/VehicleOdometry` |
| Publish | `/clawdrone/monitor/diagnostics` | `diagnostic_msgs/msg/DiagnosticArray` |

Telemetry QoS is KEEP_LAST depth 1, BEST_EFFORT, VOLATILE. Diagnostics use
RELIABLE, VOLATILE, depth 10. Dependencies are `rclpy`, `px4_msgs`,
`diagnostic_msgs`, `rcl_interfaces`, `ament_python` and Python setuptools.
Tests use pytest, `ament_flake8` and `ament_pep257`.
Use the workspace's vendored `px4_msgs` with compatible PX4 firmware/DDS output.

## Build and run

From the repository root, with dependencies already available:

```bash
source /opt/ros/humble/setup.bash
cd f550_ws
colcon build --symlink-install --packages-up-to f550_monitor
source install/setup.bash
ros2 run f550_monitor telemetry_monitor
```

The node is named `telemetry_monitor_node`. It can run without a simulator;
diagnostics will report missing telemetry. Building up to this package also
builds its local message dependency; it does not build `f550_control`.

## Parameters

All parameters are startup-only doubles. Supply decimal values with ROS arguments:

```bash
ros2 run f550_monitor telemetry_monitor --ros-args \
  -p telemetry_timeout_sec:=3.0 -p altitude_warning_m:=15.0 \
  -p speed_warning_mps:=4.0
```

| Parameter | Default | Meaning |
| --- | --- | --- |
| `telemetry_timeout_sec` | 2.0 | Maximum monotonic time without receipt |
| `altitude_warning_m` | 10.0 | Upper local altitude warning in metres |
| `speed_warning_mps` | 5.0 | Speed magnitude warning in metres/second |
| `quaternion_norm_tolerance` | 0.01 | Allowed absolute deviation of norm from 1 |

All values must be finite and positive; quaternion tolerance must also be below
1. Invalid configuration prevents startup. Thresholds trigger strictly above
the limit. **These are preliminary simulation warnings, not certified physical
safety limits.** There is no lower altitude limit or automatic safety action.

## Diagnostics and interpretation

One status is published approximately every second using a steady-clock timer,
even if simulated ROS time pauses. The header stamp uses ROS time. Routine
telemetry generates no terminal logs.

| Level | Condition |
| --- | --- |
| WARN | Waiting for the initial sample, until timeout |
| OK | Fresh, valid NED telemetry within warning limits |
| WARN | Unsupported frame or altitude/speed warning |
| ERROR | Non-finite/malformed position, velocity or quaternion; invalid norm |
| STALE | No initial sample after timeout, or last receipt older than timeout |

Staleness takes priority over invalid measurements, which take priority over
warnings. Messages retain simultaneous issues. Key/value fields contain limits,
receipt age (or initial wait duration), raw vectors, frame IDs, quaternion norm,
and valid derived NED position, velocity, altitude and speed when available.

NED local altitude is `-position[2]`, relative to the local estimator origin;
it is not height above ground or sea level. Position and velocity frames are
checked independently. Only NED is interpreted: FRD, BODY_FRD, unknown and
unrecognized frames produce warnings and omit the corresponding derived values.
Quaternion validation checks finite components in `(w,x,y,z)` order and unit norm;
it neither normalizes data nor transforms frames.

## Tests

Pure evaluation tests require only Python and pytest, with no ROS, DDS or simulator:

```bash
cd f550_ws/src/f550_monitor
PYTHONPATH="$PWD" python3 -m pytest test/test_telemetry.py
```

For the full package tests after building (from `f550_ws`):

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon test --packages-select f550_monitor --event-handlers console_direct+
colcon test-result --test-result-base build/f550_monitor --verbose
```

Tests cover valid/missing/stale data, recovery, non-finite values, quaternion
validation, threshold boundaries, configuration and unsupported frames, plus
Python style/docstrings. Adapter tests exercise real ROS message conversion and
diagnostic serialization without creating DDS participants. No simulator is
started by the tests.

## Known limitations

Timeout detects local reception loss, not measurement age: PX4 timestamps are
not synchronized or checked, so repeatedly delivered old samples appear fresh.
Only the latest received sample is evaluated; transient errors between periodic
updates may be missed. Estimator resets can change the local altitude origin.
Angular velocity, covariance, estimator health, quality, terrain clearance and
vehicle dynamics are not evaluated. No flight safety certification is implied.
Actual SITL/DDS compatibility and real-flight behavior require separate validation;
the workspace README documents a potential PX4/message revision mismatch.
