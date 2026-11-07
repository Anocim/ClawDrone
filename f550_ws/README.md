# F550 ROS 2 workspace

This workspace contains the project's ROS 2 control nodes and the PX4
interfaces required to build them.

```text
f550_ws/
├── src/
│   ├── f550_control/  # project nodes
│   └── px4_msgs/      # PX4 ROS 2 interfaces, versioned in this repository
└── README.md
```

`build/`, `install/` and `log/` are local `colcon` products. They are ignored
by Git and can be regenerated on any machine.

## Build the workspace

```bash
cd f550_ws
source /opt/ros/humble/setup.bash
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
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install
```

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
```

Run the nodes in a separate terminal from the DDS agent and PX4 SITL. The
offboard and mission nodes publish to `/fmu/in/...`; the mission node reads
PX4 state from `/fmu/out/...`.

## Verification

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon list
ros2 interface show px4_msgs/msg/VehicleCommand
ros2 topic list
```

The package list must contain `px4_msgs` and `f550_control`. Once PX4 and the
agent are running, the topic list should contain `/fmu/in/...` and
`/fmu/out/...` topics.
