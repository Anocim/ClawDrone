# f550_patas_mono_cam_down

DJI F550 with three landing legs and a downward-facing monocular camera. PX4
airframe `4055_gz_f550_patas_mono_cam_down`, run with
`make px4_sitl gz_f550_patas_mono_cam_down`.

This variant extends [`f550_patas`](../f550_patas/README.md): the `requires`
file lists `f550_patas`, so installing this variant also installs the legged
model and its self-contained meshes. See the [variants index](../README.md).

## Files

| Path | Installed into `PX4-Autopilot/` | Purpose |
|---|---|---|
| `airframe/4055_gz_f550_patas_mono_cam_down` | `ROMFS/px4fmu_common/init.d-posix/airframes/` | Sets `PX4_SIM_MODEL` and sources `4052_gz_f550_patas`, so all motor and control parameters come from the patas airframe |
| `models/f550_patas_mono_cam_down/` | `Tools/simulation/gz/models/f550_patas_mono_cam_down/` | Includes the `f550_patas` model and `model://mono_cam`, joined by `CameraJoint` |

The [patas variant's motor layout](../f550_patas/README.md#motor-layout-and-control)
applies unchanged. The leg meshes come from the base variant; the `mono_cam`
model is expected in PX4's Gazebo model path and is not bundled here.

## Install and launch

```sh
cd px4-f550-gz
./install.sh --list
./install.sh --px4 ~/PX4-Autopilot --variant f550_patas_mono_cam_down
cd ~/PX4-Autopilot
make px4_sitl gz_f550_patas_mono_cam_down
```

`--variant f550_patas` is installed automatically because of `requires`. The
`tenis` world can be selected with `PX4_GZ_WORLD=tenis`.

## Camera topics

Gazebo names the spawned model with a `_0` suffix. With the `tenis` world, the
default image topic is:

```text
/world/tenis/model/f550_patas_mono_cam_down_0/link/camera_link/sensor/camera/image
```

Confirm with `gz topic -l | grep image` (the linked
[`f550_vision`](../../../f550_ws/src/f550_vision/README.md) launch files
accept `gz_image_topic` as an override).

## Verification

Check the base airframe values (for example `param show CA_ROTOR0_PY` →
`0.275` and `param show CA_ROTOR0_KM` → `-0.06`) as documented in the
[main simulation README](../../README.md#verification), then confirm that the
Gazebo camera topic exists. No separate control-allocation parameters are
defined for this variant.

## Status

The configuration is recorded statically in this repository. The base
`f550_patas` variant has not been flight-tested (see its README); this camera
extension has no separate runtime validation record either. Check rendering,
camera delivery and ground contact in a running Gazebo session.
