# f550_vision

Downward camera support for ClawDrone's F550 simulation (ROS 2 Humble,
`ament_python`): a Gazebo-to-ROS 2 camera bridge, a small viewer and a YOLO
(Ultralytics) detector. It never publishes PX4 commands; `f550_control` and
`f550_monitor` are independent and unchanged.

Pure logic lives apart from ROS so it can be tested without a simulator:
`frame_stats.py`, `image_utils.py` and `detections.py`. The nodes only adapt
them to ROS. Images are converted with NumPy instead of `cv_bridge`, because
`cv_bridge` on Humble breaks when pip installs NumPy 2.

## Requirements

* The Gazebo-ROS bridge must match PX4's Gazebo (`gz sim --versions`). With
  Gazebo Harmonic on Humble install `ros-humble-ros-gzharmonic` (OSRF repo);
  it conflicts with the stock `ros-humble-ros-gz*` (Fortress) packages.
* `ros-humble-vision-msgs`.
* For the detector: `ultralytics` (pip), see below.

## Python environment for YOLO

```bash
python3 -m venv --system-site-packages ~/yolo_env
source ~/yolo_env/bin/activate
pip install "numpy<2"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu   # CPU only
pip install ultralytics
```

Skip the CPU index line if the machine has an NVIDIA GPU and you want CUDA.
`--system-site-packages` keeps `rclpy` visible. **Build the workspace with the
environment active** so the node executables use this Python.

## Build

```bash
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
cd f550_ws
colcon build --symlink-install --packages-select f550_vision
source install/setup.bash
```

## Run

```bash
# Camera only (bridge + frame rate report)
ros2 launch f550_vision camera.launch.py

# Camera + YOLO
ros2 launch f550_vision detector.launch.py model_path:=/abs/path/best.pt
```

Launch arguments: `world` (`tenis`), `model` (`f550_detailed_mono_cam_down_0`,
including the `_N` suffix), `link` (`camera_link`) and `sensor` (`camera`).
The bridged Gazebo topic is `/world/<world>/model/<model>/link/<link>/sensor/<sensor>/image`.
If your camera model names things differently, or the sensor sets its own
`<topic>`, pass the full topic with `gz_image_topic` (and `gz_info_topic` if
`camera_info` is not next to the image); find it with `gz topic -l | grep image`.
`camera.launch.py` also has `viewer` and `show_window`. `detector.launch.py` also has `conf_threshold` (0.4),
`target_labels` (comma separated, empty keeps all classes), `max_rate_hz` (5.0)
and `device` (empty = automatic).

## Topics

| Direction | Topic | Type |
| --- | --- | --- |
| Publish (bridge) | `/camera_down/image_raw` | `sensor_msgs/msg/Image` |
| Publish (bridge) | `/camera_down/camera_info` | `sensor_msgs/msg/CameraInfo` |
| Publish (detector) | `/camera_down/detections` | `vision_msgs/msg/Detection2DArray` |
| Publish (detector) | `/camera_down/image_annotated` | `sensor_msgs/msg/Image` (bgr8) |

Detections are in pixels of the processed image (box center and size). The
annotated image is only produced while someone subscribes to it. View it with
`ros2 run rqt_image_view rqt_image_view /camera_down/image_annotated` or an
Image display in RViz. Camera topics use sensor QoS (best effort).

## Parameters (ball_detector_node, startup only)

| Parameter | Default | Meaning |
| --- | --- | --- |
| `model_path` | (required) | Absolute path to the Ultralytics `.pt` file |
| `conf_threshold` | 0.4 | Minimum score, in (0, 1] |
| `imgsz` | 640 | Inference size |
| `device` | `''` | `''` automatic, `cpu`, or a CUDA index such as `0` |
| `max_rate_hz` | 5.0 | Frames above this rate are skipped |
| `target_labels` | `''` | Comma-separated class names to keep |

Invalid values or a missing model file prevent startup.

## Tests

```bash
colcon test --packages-select f550_vision && colcon test-result --verbose
```

The unit tests do not need ROS, a simulator or a model.
