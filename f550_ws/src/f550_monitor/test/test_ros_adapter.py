"""Check real ROS message conversion without creating a DDS participant."""

from types import SimpleNamespace

import pytest

pytest.importorskip('rclpy')
pytest.importorskip('px4_msgs.msg')

from diagnostic_msgs.msg import DiagnosticStatus  # noqa: E402
from px4_msgs.msg import VehicleOdometry  # noqa: E402
from rclpy.serialization import deserialize_message, serialize_message  # noqa: E402
from rclpy.time import Time  # noqa: E402

from f550_monitor.telemetry import MonitorConfig, TelemetryMonitor  # noqa: E402
from f550_monitor.telemetry_monitor_node import TelemetryMonitorNode  # noqa: E402


@pytest.mark.parametrize('valid,expected', [
    (True, DiagnosticStatus.OK), (False, DiagnosticStatus.ERROR),
])
def test_message_conversion_and_diagnostics(valid, expected):
    """Serialize evaluated diagnostics from real VehicleOdometry messages."""
    published = []
    adapter = SimpleNamespace(
        monitor=TelemetryMonitor(MonitorConfig()),
        get_fully_qualified_name=lambda: '/telemetry_monitor_node',
        get_clock=lambda: SimpleNamespace(now=lambda: Time(seconds=123)),
        diagnostics_publisher=SimpleNamespace(publish=published.append),
    )
    msg = VehicleOdometry()
    msg.pose_frame = VehicleOdometry.POSE_FRAME_NED
    msg.velocity_frame = VehicleOdometry.VELOCITY_FRAME_NED
    msg.position = [1.0, 2.0, -3.0]
    msg.velocity = [0.0, 0.0, 0.0]
    msg.q = [1.0 if valid else 0.0, 0.0, 0.0, 0.0]
    TelemetryMonitorNode._on_odometry(adapter, msg)
    # Changing the ROS message must not mutate the stored snapshot.
    msg.position[2] = -100.0
    TelemetryMonitorNode._publish_diagnostics(adapter)
    result = deserialize_message(serialize_message(published[0]), type(published[0]))
    assert result.header.stamp.sec == 123
    assert result.status[0].level == expected
    values = {item.key: item.value for item in result.status[0].values}
    assert float(values['local_altitude_m']) == 3.0


def test_frame_constants():
    """Ensure the standalone evaluator's NED enum matches local PX4 messages."""
    from f550_monitor.telemetry import NED

    assert NED == VehicleOdometry.POSE_FRAME_NED
    assert NED == VehicleOdometry.VELOCITY_FRAME_NED
