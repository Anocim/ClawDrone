# f550_simple

Simple DJI F550 model: primitive shapes (boxes and cylinders) instead of meshes, lighter body, same six-motor
layout. PX4 airframe `4051_gz_f550_simple`, run with `make px4_sitl gz_f550_simple`.
Use it when you want a fast, lightweight simulation or a starting point for your own model.

| Path | Installed into `PX4-Autopilot/` | Purpose |
|---|---|---|
| `airframe/4051_gz_f550_simple` | `ROMFS/px4fmu_common/init.d-posix/airframes/` | `CA_ROTORn_*` geometry, motor outputs, hover throttle |
| `models/f550_simple/` | `Tools/simulation/gz/models/f550_simple/` | Includes the base and declares the six motor plugins |
| `models/f550_base_simple/` | `Tools/simulation/gz/models/f550_base_simple/` | Body, inertia, rotors, joints, sensors (IMU, magnetometer, barometer, GPS) |

No meshes are needed: this variant does not use `third_party/`.

## Motor layout

Top view, drone facing **+X (front)**. Gazebo convention: **+Y = left**.

```
                      ^ X (front)
                      |
        rotor_5 o-----+-----o rotor_0
        (M5, CW)      |     (M0, CCW)
           FL         |         FR
                      |
  rotor_4 o-----------+-----------o rotor_1
 (M4, CCW)            |            (M1, CW)
   LEFT              -+-              RIGHT
                      |
           BL         |         BR
        (M3, CW)      |     (M2, CCW)
        rotor_3 o-----+-----o rotor_2
```

Spin directions alternate around the vehicle (CCW, CW, CCW, CW, CCW, CW).

| PX4 motor (`CA_ROTORn`) | Output function | SDF rotor | Position | Gazebo (x, y) in m | Spin | `PX` | `PY` | `KM` |
|---|---|---|---|---|---|---|---|---|
| 0 | 101 | `rotor_0` | front right | (+0.2382, -0.1375) | CCW | +0.2382 | +0.1375 | +0.05 |
| 1 | 102 | `rotor_1` | right | (0, -0.275) | CW | 0 | +0.275 | -0.05 |
| 2 | 103 | `rotor_2` | back right | (-0.2382, -0.1375) | CCW | -0.2382 | +0.1375 | +0.05 |
| 3 | 104 | `rotor_3` | back left | (-0.2382, +0.1375) | CW | -0.2382 | -0.1375 | -0.05 |
| 4 | 105 | `rotor_4` | left | (0, +0.275) | CCW | 0 | -0.275 | +0.05 |
| 5 | 106 | `rotor_5` | front left | (+0.2382, +0.1375) | CW | +0.2382 | -0.1375 | -0.05 |

Note that the motor order differs from `f550_detailed` (there motor 0 is the right-hand rotor). That is fine:
each airframe carries its own `CA_ROTORn_*`, and the make target always launches the matching airframe and model.

### Rules to respect when modifying anything

1. **The PX4 motor index is the rotor number:** `CA_ROTORn` = `<actuator_number>n</actuator_number>` = `rotor_n`.
2. **PX4 uses FRD axes, Gazebo uses FLU:** `PY(PX4) = -y(Gazebo)`. Forgetting this sign inverts roll and the drone flips on takeoff.
3. **`KM > 0` means CCW, `KM < 0` means CW**, and must match `<turningDirection>` of the same motor.
4. Spin directions of neighbouring rotors must alternate.
5. `f550_simple/model.sdf` must include `model://f550_base_simple` (not `f550_base`, which belongs to the detailed variant).

### Physical parameters

| Parameter | Value |
|---|---|
| Mass | 1.5 kg body + 6 x 16 g rotors = 1.596 kg |
| `motorConstant` | 5.2e-6 |
| `maxRotVelocity` | 1000 rad/s |
| `momentConstant` | 0.016 |
| Thrust-to-weight | about 2.0 |
| Hover | about 708 rad/s, i.e. `(708-150)/850` = 0.66 of the output. The airframe keeps `MPC_THR_HOVER 0.5` (the tested value); PX4's hover-thrust estimator adapts it in flight |

PX4 maps its output to 150-1000 rad/s (`SIM_GZ_EC_MIN/MAX`). The base model is placed at z = 0.15 m and
its collision is a 0.2 x 0.2 x 0.05 m box (the legs are visual only).

## Changing the layout

Edit `<linkName>`, `<turningDirection>` and `<actuator_number>` in `models/f550_simple/model.sdf` and the rotor poses
in `models/f550_base_simple/model.sdf`, then regenerate the parameters:

```sh
python3 tools/gen_ca.py \
  variants/f550_simple/models/f550_simple/model.sdf \
  variants/f550_simple/models/f550_base_simple/model.sdf --km 0.05
```

Paste the `param set-default CA_ROTOR...` lines into `airframe/4051_gz_f550_simple`, rerun `./install.sh`, and rebuild.
