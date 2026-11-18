"""Run an Ultralytics YOLO model on the downward camera and publish detections.

The node only observes: it publishes detections and an annotated image and
never sends PX4 commands.
"""

from pathlib import Path
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import ParameterDescriptor
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose

from f550_vision.detections import build_detections, parse_labels
from f550_vision.frame_stats import FrameStats
from f550_vision.image_utils import bgr_to_image_fields, image_fields_to_bgr


def _fill_detection(detection, header):
    """Build a ``vision_msgs/Detection2D`` from a plain detection record.

    The field layout of vision_msgs changed between releases, so both the
    older and the newer layouts are handled.
    """
    msg = Detection2D()
    msg.header = header
    center = msg.bbox.center
    if hasattr(center, 'position'):
        center.position.x = detection.center_x
        center.position.y = detection.center_y
    else:
        center.x = detection.center_x
        center.y = detection.center_y
    msg.bbox.size_x = detection.width
    msg.bbox.size_y = detection.height
    hypothesis = ObjectHypothesisWithPose()
    if hasattr(hypothesis, 'hypothesis'):
        hypothesis.hypothesis.class_id = detection.label
        hypothesis.hypothesis.score = detection.score
    else:
        hypothesis.id = detection.label
        hypothesis.score = detection.score
    msg.results.append(hypothesis)
    return msg


class BallDetectorNode(Node):
    """Detect objects in camera frames with a YOLO model."""

    def __init__(self):
        """Declare startup parameters, load the model and create the I/O."""
        super().__init__('ball_detector_node')
        read_only = ParameterDescriptor(read_only=True)

        def param(name, default):
            return self.declare_parameter(name, default, read_only).value

        model_path = param('model_path', '')
        image_topic = param('image_topic', '/camera_down/image_raw')
        detections_topic = param('detections_topic', '/camera_down/detections')
        annotated_topic = param('annotated_topic', '/camera_down/image_annotated')
        self._conf = float(param('conf_threshold', 0.4))
        self._imgsz = int(param('imgsz', 640))
        self._device = param('device', '')
        max_rate_hz = float(param('max_rate_hz', 5.0))
        self._labels = parse_labels(param('target_labels', ''))

        if not 0.0 < self._conf <= 1.0:
            raise ValueError('conf_threshold must be in (0, 1]')
        if self._imgsz <= 0 or max_rate_hz <= 0.0:
            raise ValueError('imgsz and max_rate_hz must be positive')
        if not model_path or not Path(model_path).is_file():
            raise ValueError(
                f"model_path {model_path!r} is not a file; pass -p model_path:=/abs/best.pt")
        self._min_period = 1.0 / max_rate_hz

        try:
            from ultralytics import YOLO
        except ImportError as error:
            raise RuntimeError(
                'ultralytics is not installed in the Python used by this node; '
                'see the README (virtual environment section)') from error
        self._model = YOLO(model_path)
        self.get_logger().info(
            f'Loaded {model_path}; classes: {self._model.names}')

        self._stats = FrameStats()
        self._last_run = 0.0
        self.detections_publisher = self.create_publisher(
            Detection2DArray, detections_topic, 10)
        self.annotated_publisher = self.create_publisher(Image, annotated_topic, 1)
        self.subscription = self.create_subscription(
            Image, image_topic, self._on_image, qos_profile_sensor_data)
        self.report_timer = self.create_timer(5.0, self._report)
        self.get_logger().info(
            f'Detecting on {image_topic} at up to {max_rate_hz:g} Hz; '
            f'labels: {sorted(self._labels) or "all"}')

    def _on_image(self, msg):
        """Run the model on the frame, rate-limited, and publish the results."""
        now = time.monotonic()
        if now - self._last_run < self._min_period:
            return
        self._last_run = now
        try:
            frame = image_fields_to_bgr(
                msg.data, msg.width, msg.height, msg.step, msg.encoding)
        except ValueError as error:
            self.get_logger().warn(str(error), throttle_duration_sec=5.0)
            return

        result = self._model.predict(
            frame, conf=self._conf, imgsz=self._imgsz,
            device=self._device or None, verbose=False)[0]
        boxes = result.boxes
        detections = build_detections(
            boxes.xywh.cpu().numpy(), boxes.conf.cpu().numpy(),
            boxes.cls.cpu().numpy(), result.names, self._labels)

        array = Detection2DArray()
        array.header = msg.header
        array.detections = [_fill_detection(item, msg.header) for item in detections]
        self.detections_publisher.publish(array)
        self._stats.add(time.monotonic())

        if self.annotated_publisher.get_subscription_count() > 0:
            data, width, height, step, encoding = bgr_to_image_fields(result.plot())
            annotated = Image()
            annotated.header = msg.header
            annotated.height, annotated.width = height, width
            annotated.encoding, annotated.step = encoding, step
            annotated.is_bigendian = 0
            annotated.data = data
            self.annotated_publisher.publish(annotated)

    def _report(self):
        """Log the processing rate, or warn when nothing was processed."""
        if self._stats.total == 0:
            self.get_logger().warn('No frames processed yet')
            return
        self.get_logger().info(
            f'{self._stats.total} frames processed, {self._stats.rate_hz():.1f} Hz')


def main(args=None):
    """Run the detector node until interrupted."""
    rclpy.init(args=args)
    node = BallDetectorNode()
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
