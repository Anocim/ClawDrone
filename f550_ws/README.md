# F550 ROS 2 workspace

This workspace contains the project's ROS 2 packages and the PX4 interfaces
required to build them. The Gazebo/PX4 side lives in
[`px4-f550-gz/`](../px4-f550-gz/README.md); the complete launch example is in
the [repository README](../README.md#complete-launch-example-one-terminal-per-process).

## Packages

| Package | Purpose | Documentation |
|---|---|---|
| `f550_control` | Offboard control, ball-retrieval mission and emergency override | [src/f550_control/README.md](src/f550_control/README.md) |
| `f550_monitor` | Read-only telemetry monitoring and diagnostics | [src/f550_monitor/README.md](src/f550_monitor/README.md) |
| `f550_vision` | Downward camera bridge, viewer and YOLO ball detector | [src/f550_vision/README.md](src/f550_vision/README.md) |
| `px4_msgs` | PX4 ROS 2 interfaces, vendored in this repository | [src/px4_msgs/README.md](src/px4_msgs/README.md) (upstream) |

`px4_msgs` is deliberately included as vendored source at a pinned upstream
commit, not as a Git submodule. A normal clone therefore contains the message
definitions needed by the project without initializing another repository. Its
provenance and update procedure are described below. Its own README is the
upstream PX4 documentation: the `git clone`/apt installation steps there do
**not** apply to this vendored copy.

## Layout

```text
f550_ws/
├── INSTALL.md               # dependency installation (ROS, Gazebo bridge, YOLO)
├── README.md                # this file
├── requirements-vision.txt  # pip requirements for the detector
├── scripts/
│   └── setup_vision_env.sh  # creates ~/yolo_env (see scripts/README.md)
└── src/
    ├── f550_control/
    ├── f550_monitor/
    ├── f550_vision/
    └── px4_msgs/
```

`build/`, `install/` and `log/` are local `colcon` products. They are ignored
by Git and can be regenerated on any machine. In this checkout they were also
generated under `src/`; those paths are ignored as well.

## Dependencies

Install the system and Python dependencies first:
[`INSTALL.md`](INSTALL.md). It covers the Gazebo-Harmonic ROS bridge,
`rosdep` packages and the YOLO virtual environment. The Micro XRCE-DDS Agent
is an external runtime dependency and is built outside this repository.

## Build the workspace

```bash
cd f550_ws
source /opt/ros/humble/setup.bash
# If you use f550_vision, activate ~/yolo_env before building (see INSTALL.md)
colcon build --symlink-install
source install/setup.bash
```

The workspace must contain the project source and the vendored `px4_msgs`
directory. No additional clone of `px4_msgs` is required.

## Micro XRCE-DDS Agent (external dependency)

The DDS agent is not part of this repository and must be cloned in a
directory of your choice outside the project. From that external directory:

```bash
git clone -b v2.4.2 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
cd Micro-XRCE-DDS-Agent
# v2.4.2 references the retired Fast-DDS branch "2.12.x".
sed -i 's/set(_fastdds_tag 2.12.x)/set(_fastdds_tag v2.12.2)/' CMakeLists.txt
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install
```

If `make` was already run before applying this workaround, remove only the
failed generated build directory (`rm -rf build`) and repeat the `mkdir`,
`cmake`, `make` and install commands. The required agent remains `v2.4.2`;
the change only replaces a deleted upstream branch with its `v2.12.2` release
tag.

Build the agent once. Keep its source and build directories outside the
ClawDrone checkout. For each simulation session, source the ROS 2 environment
and run:

```bash
source /opt/ros/humble/setup.bash
MicroXRCEAgent udp4 -p 8888
```

Leave the agent running while PX4 and the ROS 2 nodes are used. PX4 SITL
starts its `uxrce_dds_client` automatically and connects to UDP port `8888`.

## `px4_msgs`

`src/px4_msgs` is included as vendored source, not as a submodule. A normal
`git clone` therefore obtains the interfaces used by this project without a
second repository or a `git submodule update` step.

The origin is fixed to:

| Area | Value |
| --- | --- |
| Upstream Repo | `https://github.com/PX4/px4_msgs.git` |
| Imported commit | `2e892300d8c20d3c29e198e324a10854b40ab8d3` |
| Indicated PX4 commit by upstream | `d354c4e504d9f22096dd6e0172aab0b7a6b44beb` |

Do not edit `src/px4_msgs` by hand. When updating PX4, update these interfaces
in a separate project commit: select the compatible upstream commit, replace
the vendored tree, update this table and validate with `colcon build`. The
project history then records which PX4 interface change was adopted, and every
clone remains reproducible.

> The local PX4 checkout is `95ede794c0`; there is no `px4_msgs` synchronization
> commit published for that exact hash. Check message compatibility before
> updating the interface, or use PX4's translation node if message versions
> differ.

## Running the ROS 2 nodes

After building and sourcing this workspace:

```bash
ros2 run f550_control offboard_node
ros2 run f550_control ball_retriever_node
ros2 run f550_control safety_node

ros2 run f550_monitor telemetry_monitor

# With a *_mono_cam_down variant running in PX4/Gazebo and ~/yolo_env active:
ros2 launch f550_vision camera.launch.py
ros2 launch f550_vision detector.launch.py model_path:=/abs/path/best.pt
```

Run the nodes in separate terminals from the DDS agent and PX4 SITL; see the
[complete launch example](../README.md#complete-launch-example-one-terminal-per-process).
The control nodes publish to `/fmu/in/...`; the mission and monitor nodes read
PX4 state from `/fmu/out/...`. Parameters, topics and tests are documented in
each package README linked above.

## Verification

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon list
ros2 interface show px4_msgs/msg/VehicleCommand
ros2 topic list
```

The package list must contain `f550_control`, `f550_monitor`, `f550_vision` and
`px4_msgs`. Once PX4 and the agent are running, the topic list should contain
`/fmu/in/...` and `/fmu/out/...`.
