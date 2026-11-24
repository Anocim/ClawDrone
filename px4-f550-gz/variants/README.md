# Variants

Each folder here is one installable F550 configuration. `install.sh` discovers
every folder in this directory that contains at least one file in `airframe/`;
folders starting with `_` (such as [`_template/`](_template/README.md)) are
ignored. The script never needs editing to add a variant.

## Installable variants

| Folder | Airframe ID | Make target | Requires | Base model | README |
|---|---|---|---|---|---|
| `f550` | `4050_gz_f550` | `gz_f550` | — | — (detailed) | [f550/README.md](f550/README.md) |
| `f550_simple` | `4051_gz_f550_simple` | `gz_f550_simple` | — | — (simple) | [f550_simple/README.md](f550_simple/README.md) |
| `f550_patas` | `4052_gz_f550_patas` | `gz_f550_patas` | — | — (legged) | [f550_patas/README.md](f550_patas/README.md) |
| `f550_detailed_mono_cam_down` | `4053_gz_f550_detailed_mono_cam_down` | `gz_f550_detailed_mono_cam_down` | `f550` | detailed | [README](f550_detailed_mono_cam_down/README.md) |
| `f550_simple_mono_cam_down` | `4054_gz_f550_simple_mono_cam_down` | `gz_f550_simple_mono_cam_down` | `f550_simple` | simple | [README](f550_simple_mono_cam_down/README.md) |
| `f550_patas_mono_cam_down` | `4055_gz_f550_patas_mono_cam_down` | `gz_f550_patas_mono_cam_down` | `f550_patas` | legged | [README](f550_patas_mono_cam_down/README.md) |

Use the **folder name** with `install.sh --variant`, for example:

```bash
cd px4-f550-gz
./install.sh --list
./install.sh --px4 ~/PX4-Autopilot --variant f550
```

`--variant f550` is the detailed model; there is no folder named
`f550_detailed`. The old airframe name `4051_gz_f550` is a legacy conflict and
is removed by the installer.

## How `requires` works

A variant that extends another one lists the base folder name, one per line,
in a file called `requires` at the root of its folder. Installing
`f550_detailed_mono_cam_down` therefore also installs `f550`. Dependencies are
resolved recursively. They are **not** removed when uninstalling a single
variant; only `--variant all` removes all of them.

The camera variants include PX4's `model://mono_cam` resource. That model is
expected to exist in the PX4 checkout; it is not bundled in this repository.
The `[f550_vision](../../f550_ws/src/f550_vision/README.md)` package bridges
its image topic to ROS 2.

## Adding a variant

1. Copy [`_template/`](_template/README.md) to `variants/<name>/`.
2. Pick a free airframe ID `40NN` and make target; `install.sh` checks both.
3. Add the Gazebo models and the airframe file.
4. Add a `requires` file if the model extends another variant.
5. Add a short README following the existing ones: name, ID, target, models,
   dependencies, motor layout and validation status.

Airframe and model conventions are described in the
[`_template` README](_template/README.md); control-allocation parameters can
be generated with [`tools/gen_ca.py`](../tools/README.md).
