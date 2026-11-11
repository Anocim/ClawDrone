# Tennis World for PX4 SITL and Gazebo Sim

This directory contains the `tenis` world used for DJI F550 ball-retrieval experiments with PX4 SITL and Gazebo Sim.

The world is self-contained in `tenis.sdf`. The court, court markings, net, collection table and four tennis balls are defined with SDF geometry. No additional Gazebo model folders, meshes or textures are required to load this world.

## World contents

### Tennis court

The court uses standard doubles dimensions:

| Property | Value |
|---|---:|
| Length | 23.77 m |
| Doubles width | 10.97 m |
| Ground plane | 100 × 100 m |
| Ground appearance | Green |

The court markings include the doubles boundary, singles sidelines, service lines, centre service line and baseline centre marks. The markings are visual only and do not create physical obstacles.

The complete court layout is translated by **+5.9425 m along world X**. This keeps the world origin `(0, 0, 0)` near the first quarter of the court, where the F550 spawns, and places the net at the court's longitudinal midpoint.

### Tennis net

The net is centred at world position `(5.9425, 0, 0)`. It includes side posts, a top tape and a geometric representation of the net. A thin collision volume prevents objects from passing straight through it. The net is a rigid simulation object, not a deformable fabric mesh.

### Tennis balls

Four dynamic tennis balls are included. Each ball has a radius of 0.033 m and a mass of 0.058 kg.

Initial world positions:

| Entity | X (m) | Y (m) | Z (m) |
|---|---:|---:|---:|
| `pelota_1` | 8.9425 | 2.0 | 0.033 |
| `pelota_2` | 10.9425 | -1.0 | 0.033 |
| `pelota_3` | -1.0575 | -3.0 | 0.033 |
| `pelota_4` | -3.0575 | 3.4 | 0.033 |

The balls have collision geometry and can move when contacted.

### Ball collection table

A fixed collection table is positioned outside the negative-Y sideline, centred at `(0, -7.2, 0)`.

| Property | Value |
|---|---:|
| Tabletop size | 2.60 × 1.50 m |
| Tabletop upper surface | 0.85 m above the ground |
| Structure | Tabletop, four legs and support frame |
| Physics | Static model with collision geometry |

The tabletop is sized to provide room for all four tennis balls.

## Coordinate frames

The Gazebo world uses ENU coordinates:

- X: East
- Y: North
- Z: Up

The original spherical-coordinate reference is preserved:

| Property | Value |
|---|---:|
| Latitude | 37.3828° |
| Longitude | -5.9731° |
| Elevation | 10 m |
| World-frame orientation | ENU |

PX4 trajectory setpoints use NED coordinates (North, East, Down). The project's `ball_retriever_node` asks for ball and drop-off X/Y in Gazebo world coordinates (East, North) and converts their order for PX4 internally. Its Z input follows NED convention, where positive values point downwards.

## Requirements

- Ubuntu 22.04 (or a compatible Gazebo Sim environment)
- Gazebo Sim 8, as used by the project setup
- PX4 SITL and the F550 airframe/model installation when running the drone in the world

The world can also be opened in Gazebo without PX4.

## Installation

Copy `tenis.sdf` into the PX4 Gazebo worlds directory:

```bash
mkdir -p ~/Firmware/Tools/simulation/gz/worlds
cp tenis.sdf ~/Firmware/Tools/simulation/gz/worlds/tenis.sdf
```

No additional model installation is required for the court, net, table or balls; they are defined in the SDF file.

## Run Gazebo without PX4

```bash
gz sim -r ~/Firmware/Tools/simulation/gz/worlds/tenis.sdf
```

This starts Gazebo with the tennis world only.

## Run with PX4 SITL and the F550

The F550 model and its PX4 airframe must already be installed in the PX4 checkout. From the PX4 directory, run:

```bash
cd ~/Firmware
PX4_GZ_WORLD=tenis make px4_sitl gz_f550
```

## Inspect world entities

While Gazebo is running, inspect entity poses with:

```bash
gz topic -e -t /world/tenis/pose/info
```

Look for `tennis_court_lines`, `tennis_net`, `ball_collection_table` and `pelota_1` through `pelota_4`.

## Ball-retrieval node notes

The current `ball_retriever_node` asks the operator to enter the ball coordinates and drop-off coordinates in the terminal. It does not automatically detect the balls or read their poses from Gazebo. The current pickup and drop-off stages use timed pauses; there is no physical gripper or sensor-based confirmation that a ball has been picked up or released.

Use the initial positions in the table above as the ball coordinates when setting up a test mission. The drop-off coordinates should be selected on the table surface, taking care to use the coordinate conventions described above.

## Limitations

- Court lines are visual markings only.
- The net and table are rigid objects with collision geometry.
- The balls are dynamic and physically collidable.
- The world file has been checked for valid SDF/XML structure; it still needs to be run in the target Gazebo installation to verify rendering and physics behaviour there.
