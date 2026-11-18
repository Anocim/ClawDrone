# f550_detailed

Detailed DJI F550 model. PX4 airframe `4050_gz_f550`, run with `make px4_sitl gz_f550`.

| Path | Installed into `PX4-Autopilot/` | Purpose |
|---|---|---|
| `airframe/4050_gz_f550` | `ROMFS/px4fmu_common/init.d-posix/airframes/` | `CA_ROTORn_*` geometry, motor outputs, hover throttle, spawn pose |
| `models/f550/` | `Tools/simulation/gz/models/f550/` | Includes the base and declares the six motor plugins |
| `models/f550_base/` | `Tools/simulation/gz/models/f550_base/` | Rigid body, inertia, propellers, joints, sensors (IMU, magnetometer, barometer, GPS) |

The visuals use the meshes bundled in `third_party/mrs_robots_description/` (installed automatically; visual only).

## Motor layout

Top view, drone facing **+X (front)**. Gazebo convention: **+Y = left**.

```
                      ^ X (front)
                      |
         prop_2 o-----+-----o prop_4
        (M2, CCW)     |     (M4, CW)
           FL         |         FR
                      |
   prop_1 o-----------+-----------o prop_0
  (M1, CW)            |            (M0, CCW)
   LEFT              -+-              RIGHT
                      |
           BL         |         BR
        (M5, CCW)     |     (M3, CW)
         prop_5 o-----+-----o prop_3
```

Spin directions alternate around the vehicle (CCW, CW, CCW, CW, CCW, CW), as on a real F550.

| PX4 motor (`CA_ROTORn`) | Output function | SDF propeller | Position | Gazebo (x, y) in m | Spin | `PX` | `PY` | `KM` |
|---|---|---|---|---|---|---|---|---|
| 0 | 101 | `prop_0` | right | (0, -0.275) | CCW | 0 | +0.275 | +0.06 |
| 1 | 102 | `prop_1` | left | (0, +0.275) | CW | 0 | -0.275 | -0.06 |
| 2 | 103 | `prop_2` | front left | (+0.2382, +0.1375) | CCW | +0.2382 | -0.1375 | +0.06 |
| 3 | 104 | `prop_3` | back right | (-0.2382, -0.1375) | CW | -0.2382 | +0.1375 | -0.06 |
| 4 | 105 | `prop_4` | front right | (+0.2382, -0.1375) | CW | +0.2382 | +0.1375 | -0.06 |
| 5 | 106 | `prop_5` | back left | (-0.2382, +0.1375) | CCW | -0.2382 | -0.1375 | +0.06 |

### Rules to respect when modifying anything

1. **The PX4 motor index is the propeller number:** `CA_ROTORn` = `<actuator_number>n</actuator_number>` = `prop_n`.
2. **PX4 uses FRD axes, Gazebo uses FLU:** `PY(PX4) = -y(Gazebo)`. Forgetting this sign inverts roll and the drone flips on takeoff.
3. **`KM > 0` means CCW, `KM < 0` means CW**, and must match `<turningDirection>` of the same motor.
   Its magnitude (0.06) should equal `<momentConstant>`.
4. Spin directions of neighbouring propellers must alternate.

### Physical parameters

Mass 2.0 kg (+ 6 x 5 g propellers), `motorConstant` 1.05e-5, `maxRotVelocity` 1100 rad/s.
PX4 maps its output to 150-1000 rad/s, so hover is at about 0.49 of the output (`MPC_THR_HOVER 0.5`).
The vehicle spawns at z = 0.15 m (`PX4_GZ_MODEL_POSE`); the model has no landing gear collisions, only a body disc.

## Changing the layout

Edit `<linkName>`, `<turningDirection>` and `<actuator_number>` in `models/f550/model.sdf` and the propeller
poses in `models/f550_base/model.sdf`, then regenerate the parameters:

```sh
python3 tools/gen_ca.py \
  variants/f550_detailed/models/f550/model.sdf \
  variants/f550_detailed/models/f550_base/model.sdf --km 0.06
```

Paste the `param set-default CA_ROTOR...` lines into `airframe/4050_gz_f550`, rerun `./install.sh`, and rebuild.
If your physical `actuator_test` observations disagree with the SDF, use `--observed` (see `tools/gen_ca.py --help`).
