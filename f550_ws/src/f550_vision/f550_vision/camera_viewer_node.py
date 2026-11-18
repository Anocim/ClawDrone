"""Subscribe to the bridged downward camera and report or display frames."""

import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import ParameterDescriptor
from sensor_msgs.msg import Image

from f550_vision.frame_stats import FrameStats
from f550_vision.image_utils import image_fields_to_bgr


class CameraViewerNode(Node):
    """Log the camera frame rate and optionally show a preview window."""

    def __init__(self):
        """Declare startup parameters and subscribe to the image topic."""
        super().__init__('camera_viewer_node')
        read_only = ParameterDescriptor(read_only=True)
        topic = self.declare_parameter(
            'topic', '/camera_down/image_raw', read_only).value
        self._show = self.declare_parameter(
            'show_window', False, read_only).value
        self._stats = FrameStats()
        self._cv2 = None
        if self._show:
            # Imported only when needed so the node also runs without a display.
            import cv2
            self._cv2 = cv2
        self.subscription = self.create_subscription(
            Image, topic, self._on_image, qos_profile_sensor_data)
        self.report_timer = self.create_timer(5.0, self._report)
        self.get_logger().info(f'Listening to {topic} (show_window={self._show})')

    def _on_image(self, msg):
        """Count the frame and, if requested, display it."""
        self._stats.add(time.monotonic())
        if not self._show:
            return
        try:
            frame = image_fields_to_bgr(
                msg.data, msg.width, msg.height, msg.step, msg.encoding)
        except ValueError as error:
            self.get_logger().warn(str(error), throttle_duration_sec=5.0)
            return
        self._cv2.namedWindow('camera_down', self._cv2.WINDOW_NORMAL)
        self._cv2.imshow('camera_down', frame)
        self._cv2.waitKey(1)

    def _report(self):
        """Log the measured rate, or warn when no frame has arrived."""
        if self._stats.total == 0:
            self.get_logger().warn('No frames received yet')
            return
        self.get_logger().info(
            f'{self._stats.total} frames, {self._stats.rate_hz():.1f} Hz')


def main(args=None):
    """Run the viewer node until interrupted."""
    rclpy.init(args=args)
    node = CameraViewerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
