# f550_control

Python ROS 2 nodes that command the F550 in offboard mode. This package
publishes PX4 commands; it does not depend on `f550_vision` or `f550_monitor`.
Interfaces come from the vendored `px4_msgs`.

## Nodes

| Executable | Node name | Behaviour |
|---|---|---|
| `offboard_node` | `offboard_hybrid_control` | Publishes offboard mode and position setpoints at 10 Hz, requests OFFBOARD and arms automatically, then accepts keyboard input (arrow keys to move, `w`/`s` for altitude, `c` to enter exact X Y Z coordinates, `q` to quit) |
| `ball_retriever_node` | `ball_retriever_node` | Timed ball-retrieval mission: takes off, flies to operator-entered ball coordinates and drop-off coordinates, then lands and disarms. Coordinates are entered in the terminal; see [`worlds/README.md`](../../../px4-f550-gz/worlds/README.md) for the `tenis` world conventions |
| `safety_node` | `safety_node` | Subscribes to `/emergency_override` (`std_msgs/msg/Bool`); when it receives `true`, sends a mode change to POSITION to abort autonomy |

## Topics

| Direction | Topic | Type |
|---|---|---|
| Publish | `/fmu/in/offboard_control_mode` | `px4_msgs/msg/OffboardControlMode` |
| Publish | `/fmu/in/trajectory_setpoint` | `px4_msgs/msg/TrajectorySetpoint` |
| Publish | `/fmu/in/vehicle_command` | `px4_msgs/msg/VehicleCommand` |
| Subscribe (mission) | `/fmu/out/vehicle_local_position`, `/fmu/out/vehicle_local_position_v1` | `px4_msgs/msg/VehicleLocalPosition` |
| Subscribe (mission) | `/fmu/out/vehicle_odometry` | `px4_msgs/msg/VehicleOdometry` |
| Subscribe (mission) | `/fmu/out/vehicle_land_detected` | `px4_msgs/msg/VehicleLandDetected` |
| Subscribe (mission) | `/fmu/out/vehicle_status` | `px4_msgs/msg/VehicleStatus` |
| Subscribe (safety) | `/emergency_override` | `std_msgs/msg/Bool` |

PX4 telemetry topics use best-effort, volatile, depth-1 QoS.

## Build and run

```bash
# From f550_ws/
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to f550_control
source install/setup.bash

ros2 run f550_control offboard_node
# or: ros2 run f550_control ball_retriever_node
# or: ros2 run f550_control safety_node
```

Each node runs in its own terminal, with the DDS agent and PX4 SITL already
running. See the
[complete launch example](../../../README.md#complete-launch-example-one-terminal-per-process)
for the full sequence. The offboard node needs an interactive terminal for its
keyboard controls.

## Notes

- `ball_retriever_node` does not detect balls automatically and has no gripper
  feedback: pickup and drop-off are timed pauses. Ball and drop-off positions
  are entered in Gazebo world coordinates; Z follows PX4's NED convention.
- `safety_node` changes the flight mode; it does not arm, disarm or land by
  itself. The commented landing command in the source is not active.
- The package has no ROS parameters; all targets and speeds are constants in
  the source files.
