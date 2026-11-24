# ClawDrone

Simulation and control stack for a DJI F550 hexacopter: PX4 SITL + Gazebo Sim
models, and a ROS 2 Humble workspace for offboard control, telemetry monitoring
and downward-camera perception.

> **Tested with:**
> - Ubuntu 22.04.5 LTS
> - PX4-Autopilot `95ede794c0` (`v1.18.0-beta1-1084-g95ede794c0`)
> - Gazebo Sim 8.10.0 (Harmonic)
> - ROS 2 Humble
> - Micro-XRCE-DDS Agent `v2.4.2`
> - Vendored `px4_msgs` commit `2e892300d8c20d3c29e198e324a10854b40ab8d3`

This repository lives on the `Simulation_Control` branch.

## Repository structure

This README is the entry point. Each directory contains the detailed
instructions for its own part of the project:

| Path | What it contains | Detailed documentation |
|---|---|---|
| `px4-f550-gz/` | Gazebo models, PX4 airframes, installer, worlds, bundled meshes | [px4-f550-gz/README.md](px4-f550-gz/README.md) |
| `px4-f550-gz/variants/` | Six installable F550 variants plus the template | [variants/README.md](px4-f550-gz/variants/README.md) |
| `px4-f550-gz/worlds/` | `tenis` world for the ball-retrieval experiments | [worlds/README.md](px4-f550-gz/worlds/README.md) |
| `f550_ws/` | ROS 2 workspace: control, monitor, vision and vendored `px4_msgs` | [f550_ws/README.md](f550_ws/README.md) |
| `f550_ws/INSTALL.md` | Dependency installation (ROS, Gazebo bridge, YOLO environment) | [f550_ws/INSTALL.md](f550_ws/INSTALL.md) |

```text
ClawDrone/
|-- README.md                    # this file: overview, map and launch example
|-- px4-f550-gz/                 # simulation side (what is installed into PX4)
|   |-- install.sh               # installs models, airframes, meshes and worlds into PX4
|   |-- tools/                   # control-allocation parameter generator
|   |-- variants/                # one folder per F550 variant
|   |-- worlds/                  # tennis world
|   `-- third_party/             # bundled MRS meshes and their license
`-- f550_ws/                     # ROS 2 side
    |-- INSTALL.md               # dependency installation
    |-- requirements-vision.txt  # pip requirements for the detector
    |-- scripts/                 # helper scripts (YOLO environment)
    `-- src/                     # f550_control, f550_monitor, f550_vision, px4_msgs
```

`build/`, `install/` and `log/` are local colcon products and are not
versioned. `px4_msgs` is vendored source in this repository, not a submodule.

## Variants at a glance

Each variant has its own airframe ID and make target, so they can all be
installed together and selected at launch time. Camera variants list the base
variant they depend on; `install.sh` installs it automatically.

| Variant folder | Airframe ID | Make target | Requires | Description |
|---|---|---|---|---|
| `variants/f550` | `4050_gz_f550` | `gz_f550` | — | Detailed model: 3D meshes, 2.03 kg, one motor plugin per propeller |
| `variants/f550_simple` | `4051_gz_f550_simple` | `gz_f550_simple` | — | Simple model: primitive shapes, 1.596 kg, same sensors |
| `variants/f550_patas` | `4052_gz_f550_patas` | `gz_f550_patas` | — | Detailed model with three landing legs; self-contained meshes |
| `variants/f550_detailed_mono_cam_down` | `4053_gz_f550_detailed_mono_cam_down` | `gz_f550_detailed_mono_cam_down` | `f550` | Detailed model with a downward-facing camera |
| `variants/f550_simple_mono_cam_down` | `4054_gz_f550_simple_mono_cam_down` | `gz_f550_simple_mono_cam_down` | `f550_simple` | Simple model with a downward-facing camera |
| `variants/f550_patas_mono_cam_down` | `4055_gz_f550_patas_mono_cam_down` | `gz_f550_patas_mono_cam_down` | `f550_patas` | Patas model with a downward-facing camera |

Run `./install.sh --list` from `px4-f550-gz/` to see the same information.
Use the **folder name** with `--variant` (for example `--variant f550`, not
`--variant f550_detailed`).

## Quick start (high level)

1. Install the ROS 2, Gazebo bridge and Python dependencies:
   [f550_ws/INSTALL.md](f550_ws/INSTALL.md).
2. Set up PX4-Autopilot and install the models, airframes, meshes and worlds:
   [px4-f550-gz/README.md](px4-f550-gz/README.md).
3. Build and source the ROS 2 workspace:
   [f550_ws/README.md](f550_ws/README.md).
4. Build the Micro XRCE-DDS Agent **outside** this repository (version
   `v2.4.2`; exact commands in [f550_ws/README.md](f550_ws/README.md#micro-xrce-dds-agent-external-dependency)).
5. Launch the complete system with the terminals below.

## Complete launch example (one terminal per process)

Run the steps in this order. Terminals 1-3 are the core system; terminals 4-5
are optional additions for perception and monitoring.

**Terminal 1 — Micro XRCE-DDS Agent** (built outside this repository):

```sh
source /opt/ros/humble/setup.bash
MicroXRCEAgent udp4 -p 8888
```

**Terminal 2 — PX4 SITL + Gazebo Sim:**

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550                # detailed model

# Other targets:
# make px4_sitl gz_f550_simple
# make px4_sitl gz_f550_patas
# make px4_sitl gz_f550_detailed_mono_cam_down
# PX4_GZ_WORLD=tenis make px4_sitl gz_f550   # tennis world
```

**Terminal 3 — ROS 2 control node:**

```sh
cd ~/ClawDrone/f550_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run f550_control offboard_node
# or: ros2 run f550_control ball_retriever_node
# or: ros2 run f550_control safety_node
```

PX4 SITL starts its uXRCE-DDS client automatically and connects to the agent
on UDP port `8888`. In the PX4 shell (`pxh>`), `commander arm` and
`commander takeoff` are available for manual flying; the offboard node arms and
sets its own mode.

**Terminal 4 — camera bridge or YOLO detector** (optional, needs a camera
variant such as `gz_f550_detailed_mono_cam_down` in terminal 2):

```sh
source ~/yolo_env/bin/activate
cd ~/ClawDrone/f550_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch f550_vision camera.launch.py
# or: ros2 launch f550_vision detector.launch.py model_path:=/abs/path/best.pt
```

**Terminal 5 — telemetry monitor** (optional):

```sh
cd ~/ClawDrone/f550_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run f550_monitor telemetry_monitor
```

**Quick check** from any sourced ROS 2 terminal:

```sh
ros2 topic list        # expect /fmu/in/... and /fmu/out/... while PX4 runs
colcon list            # expect f550_control, f550_monitor, f550_vision, px4_msgs
```

See [f550_ws/README.md](f550_ws/README.md) for node parameters and topics, and
[px4-f550-gz/README.md](px4-f550-gz/README.md) for verification and
troubleshooting of the simulation.

## Compatibility notes

- The local PX4 checkout is `95ede794c0`. The vendored `px4_msgs` snapshot was
  imported from upstream commit `2e892300d8c20d3c29e198e324a10854b40ab8d3`,
  for which upstream indicates PX4 `d354c4e504d9f22096dd6e0172aab0b7a6b44beb`.
  There is no published `px4_msgs` synchronization commit for the exact local
  PX4 hash: check message compatibility before updating either side, or use
  PX4's translation node if the versions differ.
- The `f550_patas` variant was statically reviewed against PX4
  `v1.18.0-beta1-1230-g989a01382b`; that is not a runtime compatibility
  guarantee. Its README records the checks still pending.
- The DDS agent references a retired Fast-DDS branch; the installation pages
  document the `2.12.x` → `v2.12.2` workaround needed for `v2.4.2`.

## Development status

The current development environment supports PX4 SITL, Gazebo Sim 8, the
detailed, simple and legged DJI F550 models, their downward-camera variants, a
tennis world and a ROS 2 Humble installation with control, monitoring and
vision packages. Further work focuses on developing and testing the vehicle
control and ball-detection system within this simulation setup.

## References

- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
- [PX4 Gazebo Simulation](https://docs.px4.io/main/en/sim_gazebo_gz/)
- [Gazebo Sim](https://gazebosim.org/docs)
- [ROS 2 Humble](https://docs.ros.org/en/humble/)
- [Micro XRCE-DDS Agent](https://github.com/eProsima/Micro-XRCE-DDS-Agent)

## License and credits

The bundled MRS mesh resources are distributed under their BSD-3-Clause
license, included in `px4-f550-gz/third_party/mrs_robots_description/`. Based
on the DJI F550 description from the MRS group (CTU in Prague). Refer to the
license files before redistributing third-party resources. The vendored
`px4_msgs` tree keeps its own upstream license and documentation.
