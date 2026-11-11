"""Adapt read-only PX4 odometry monitoring to ROS 2 diagnostics."""

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from px4_msgs.msg import VehicleOdometry
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from rcl_interfaces.msg import ParameterDescriptor

from f550_monitor.telemetry import MonitorConfig, TelemetryMonitor, TelemetrySample


class TelemetryMonitorNode(Node):
    """Subscribe to telemetry and publish diagnostics; never issue commands."""

    def __init__(self):
        """Configure startup limits and a one-second steady-clock timer."""
        super().__init__('telemetry_monitor_node')
        defaults = MonitorConfig()
        parameters = {}
        for name, default in vars(defaults).items():
            parameters[name] = self.declare_parameter(
                name, default, ParameterDescriptor(read_only=True),
            ).value
        self.monitor = TelemetryMonitor(MonitorConfig(**parameters))
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )
        self.odometry_subscription = self.create_subscription(
            VehicleOdometry, '/fmu/out/vehicle_odometry', self._on_odometry, qos,
        )
        self.diagnostics_publisher = self.create_publisher(
            DiagnosticArray, '/clawdrone/monitor/diagnostics', 10,
        )
        self._steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.diagnostic_timer = self.create_timer(
            1.0, self._publish_diagnostics, clock=self._steady_clock,
        )

    def _on_odometry(self, msg):
        self.monitor.receive(TelemetrySample(
            position=tuple(msg.position),
            velocity=tuple(msg.velocity),
            quaternion=tuple(msg.q),
            pose_frame=msg.pose_frame,
            velocity_frame=msg.velocity_frame,
        ))

    def _publish_diagnostics(self):
        evaluation = self.monitor.evaluate()
        status = DiagnosticStatus(
            # Humble maps the ROS `byte` level field to a one-byte Python value.
            level=bytes([evaluation.level]),
            name=f'{self.get_fully_qualified_name()}: telemetry',
            hardware_id='f550_px4',
            message=evaluation.message,
            values=[KeyValue(key=k, value=v) for k, v in evaluation.values.items()],
        )
        diagnostics = DiagnosticArray()
        diagnostics.header.stamp = self.get_clock().now().to_msg()
        diagnostics.status = [status]
        self.diagnostics_publisher.publish(diagnostics)


def main(args=None):
    """Run the monitor until shutdown, releasing ROS resources on exit."""
    rclpy.init(args=args)
    node = None
    try:
        node = TelemetryMonitorNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
