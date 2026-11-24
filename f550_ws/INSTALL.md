# Installing the workspace dependencies

Dependencies come from four places. Each one has its own mechanism, so each
one is listed where its tool expects it. See the
[repository README](../README.md#complete-launch-example-one-terminal-per-process)
for the complete launch example once everything is installed.

| What | Where it is declared | Installed with |
| --- | --- | --- |
| ROS packages and system libraries used by a package (`vision_msgs`, `python3-numpy`, ...) | `<exec_depend>` in each `package.xml` | `rosdep` |
| Gazebo-ROS bridge for Gazebo Harmonic | this file (OSRF repository) | `apt`, by hand |
| Python packages for YOLO (`ultralytics`, `numpy<2`, `torch`) | `requirements-vision.txt` | `scripts/setup_vision_env.sh` |
| PX4 models, airframes, meshes and worlds | `variants/`, `third_party/` and `worlds/` of **this** repository (`px4-f550-gz/`) | `px4-f550-gz/install.sh` |

## 1. Gazebo-ROS bridge (Gazebo Harmonic + ROS 2 Humble)

The stock `ros-humble-ros-gz*` packages target Gazebo Fortress. For Harmonic use
the OSRF packages; they replace `ros-humble-ros-gz-interfaces`.

```bash
sudo apt install ros-humble-ros-gzharmonic
source /opt/ros/humble/setup.bash
ldd $(ros2 pkg prefix ros_gz_bridge)/lib/ros_gz_bridge/parameter_bridge | grep -i transport
# expected: gz-transport13
```

## 2. ROS dependencies with rosdep

```bash
sudo rosdep init        # only once per machine; fails harmlessly if already done
rosdep update
cd f550_ws
rosdep install --from-paths src --ignore-src -r -y --skip-keys ros_gz_bridge
```

`--skip-keys ros_gz_bridge` is required: rosdep would otherwise install the
Fortress bridge over the Harmonic one from step 1.

## 3. Python environment for the detector

```bash
sudo apt install python3.10-venv
scripts/setup_vision_env.sh            # CPU-only PyTorch; add --cuda for NVIDIA
source ~/yolo_env/bin/activate
python3 -c "from ultralytics import YOLO; print(YOLO('/abs/path/best.pt').names)"
```

Model weights (`*.pt`) are large and must not be committed; keep them outside
the repository and pass their path with `model_path:=`.

## 4. Build the workspace (environment active)

```bash
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
cd f550_ws
colcon build --symlink-install
source install/setup.bash
```

## 5. PX4 side

From this repository, run the installer with the PX4 checkout as an argument.
It copies the models, airframes, bundled meshes and the `tenis` world, and
registers the make targets:

```bash
cd ClawDrone/px4-f550-gz
./install.sh --list
./install.sh --px4 ~/PX4-Autopilot
```

See [px4-f550-gz/README.md](../px4-f550-gz/README.md#installation) for all
options, the list of variants and the manual equivalent.
