# mrs_robots_description (bundled meshes)

3D meshes used **only for the visuals** of the `f550_detailed` variant. Physics does not depend on them.

- **Source:** https://github.com/ctu-mrs/mrs_uav_gazebo_simulation, path `models/mrs_robots_description/`
- **Branch / commit copied:** `ros2` / `6a884e71d6d73c681f5d64398c3b908077641838`
- **Author:** Multi-robot Systems (MRS) group, Czech Technical University in Prague
- **License:** BSD 3-Clause, see [LICENSE](LICENSE) in this folder. Redistribution requires keeping that
  copyright notice and license text, which is why this folder must be kept together with its LICENSE.
- **Files (unmodified, only the ones the SDF files reference):**
  - `meshes/dji/f550/dji_f550_arm.dae`
  - `meshes/dji/f550/dji_f550_central_board.dae`
  - `meshes/dji/f550/dji_f550_nuc.dae`
  - `meshes/dji/f550/dji_f550_prop.dae`
  - `meshes/sensors/pixhawk.dae`

`install.sh` copies this folder to `PX4-Autopilot/Tools/simulation/gz/models/mrs_robots_description/`
so that the `model://mrs_robots_description/meshes/...` URIs in the SDF files resolve.
Need other meshes (legs, lidar mounts, ...)? Copy them from the upstream repository above, keeping the same sub-paths.
