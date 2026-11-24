# f550_detailed_mono_cam_down

Detailed DJI F550 with a downward-facing monocular camera. PX4 airframe
`4053_gz_f550_detailed_mono_cam_down`, run with
`make px4_sitl gz_f550_detailed_mono_cam_down`.

This variant extends [`f550`](../f550/README.md): the `requires` file lists
`f550`, so installing this variant also installs the detailed model and its
bundled meshes. See the [variants index](../README.md).

## Files

| Path | Installed into `PX4-Autopilot/` | Purpose |
|---|---|---|
| `airframe/4053_gz_f550_detailed_mono_cam_down` | `ROMFS/px4fmu_common/init.d-posix/airframes/` | Sets `PX4_SIM_MODEL` and sources `4050_gz_f550`, so all motor and control parameters come from the detailed airframe |
| `models/f550_detailed_mono_cam_down/` | `Tools/simulation/gz/models/f550_detailed_mono_cam_down/` | Includes the `f550` model and `model://mono_cam`, joined by `CameraJoint` |

The airframe does not duplicate `CA_ROTORn_*`: it sources the base airframe,
so the [detailed variant's motor layout](../f550/README.md#motor-layout)
applies unchanged. No meshes are bundled here: the `mono_cam` model is expected
in PX4's Gazebo model path and the detailed body uses the shared
`third_party/mrs_robots_description` meshes installed with `f550`.

## Install and launch

```sh
cd px4-f550-gz
./install.sh --list
./install.sh --px4 ~/PX4-Autopilot --variant f550_detailed_mono_cam_down
cd ~/PX4-Autopilot
make px4_sitl gz_f550_detailed_mono_cam_down
```

`--variant f550` is installed automatically because of `requires`. The `tenis`
world can be selected with `PX4_GZ_WORLD=tenis`.

## Camera topics

Gazebo names the spawned model with a `_0` suffix. With the `tenis` world, the
default image topic is:

```text
/world/tenis/model/f550_detailed_mono_cam_down_0/link/camera_link/sensor/camera/image
```

Confirm with `gz topic -l | grep image`. The ROS 2 bridge defaults in
[`f550_vision`](../../../f550_ws/src/f550_vision/README.md) match this name;
override `world`, `model`, `link`, `sensor` or the full `gz_image_topic` launch
argument if your model names differ.

## Verification

Check the base airframe values (for example `param show CA_ROTOR0_PY` →
`0.275`) as documented in the
[main simulation README](../../README.md#verification), then confirm that the
Gazebo camera topic exists. No separate control-allocation parameters are
defined for this variant.

## Status

The configuration is recorded statically in this repository; no dedicated
flight-test or rendering-validation record for this variant is included.
Camera rendering and the bridge must be checked in a running Gazebo session.
