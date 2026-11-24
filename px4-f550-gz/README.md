# px4-f550-gz

Gazebo Sim models of the DJI F550 for PX4 SITL: six installable variants, their
PX4 airframes, a tennis world and an installer that integrates them into a
PX4-Autopilot checkout.

This is the **simulation side** of the project. For the ROS 2 side, see
[`f550_ws/README.md`](../f550_ws/README.md); for the complete launch example,
see the [repository README](../README.md#complete-launch-example-one-terminal-per-process).

> **Tested with:**
> - Ubuntu 22.04.5 LTS
> - PX4-Autopilot `95ede794c0` (`v1.18.0-beta1-1084-g95ede794c0`)
> - Gazebo Sim 8.10.0 (Harmonic)
> - ROS 2 Humble (installed in the development environment)

## Subdirectories

| Directory | Purpose |
|---|---|
| [`variants/`](variants/README.md) | One folder per F550 variant: airframe files, Gazebo models and a short README |
| [`worlds/`](worlds/README.md) | `tenis.sdf`, the tennis court used for ball-retrieval experiments |
| [`tools/`](tools/README.md) | `gen_ca.py`, generates PX4 control-allocation parameters from an SDF |
| [`third_party/mrs_robots_description/`](third_party/mrs_robots_description/README.md) | Bundled CTU MRS meshes (BSD-3-Clause) used by the detailed visuals only |
| `install.sh` | Copies models, airframes, meshes and worlds into PX4 and registers the make targets |

## Variants and make targets

Each variant has its own airframe ID and make target, so all of them can be
installed together and chosen at launch time. Camera variants declare a
`requires` file: the installer adds their base variant automatically.

| Variant folder | PX4 airframe | Make target | Requires | Description |
|---|---|---|---|---|
| `f550` | `4050_gz_f550` | `make px4_sitl gz_f550` | — | Detailed model: meshes, 2.03 kg, one motor plugin per propeller |
| `f550_simple` | `4051_gz_f550_simple` | `make px4_sitl gz_f550_simple` | — | Simple model: primitive shapes, 1.596 kg, same sensors |
| `f550_patas` | `4052_gz_f550_patas` | `make px4_sitl gz_f550_patas` | — | Detailed model with three landing legs and self-contained meshes |
| `f550_detailed_mono_cam_down` | `4053_gz_f550_detailed_mono_cam_down` | `make px4_sitl gz_f550_detailed_mono_cam_down` | `f550` | Detailed model with a downward-facing camera |
| `f550_simple_mono_cam_down` | `4054_gz_f550_simple_mono_cam_down` | `make px4_sitl gz_f550_simple_mono_cam_down` | `f550_simple` | Simple model with a downward-facing camera |
| `f550_patas_mono_cam_down` | `4055_gz_f550_patas_mono_cam_down` | `make px4_sitl gz_f550_patas_mono_cam_down` | `f550_patas` | Patas model with a downward-facing camera |

Comparison of the three base models:

| | `f550` (detailed) | `f550_simple` | `f550_patas` |
|---|---|---|---|
| Visuals | CTU-MRS meshes (`third_party/`) | Boxes and cylinders | Self-contained local meshes |
| Mass | 2.03 kg | 1.596 kg | 2.03 kg |
| `motorConstant` / `maxRotVelocity` | 1.05e-5 / 1100 rad/s | 5.2e-6 / 1000 rad/s | 1.05e-5 / 1100 rad/s |
| Thrust-to-weight | about 3.8 | about 2.0 | see variant README |
| `KM` | +/-0.06 | +/-0.05 | +/-0.06 |
| Motor 0 is the... | right rotor | front-right rotor | right rotor |

Motor layouts, tables and parameters of each variant are documented in
[`variants/<name>/README.md`](variants/README.md).
`./install.sh --list` prints the variants and their make targets.

## Installation

### 1. PX4-Autopilot setup

```sh
git clone --recursive https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot
cd ~/PX4-Autopilot

git checkout 95ede794c0
git submodule update --init --recursive

bash Tools/setup/ubuntu.sh        # PX4 dependencies (log out/in if asked)
make px4_sitl gz_x500             # sanity check: the stock simulation must work first
```

If the standard simulation does not launch, check the PX4 and Gazebo
installation first.

### 2. Clone this repository

```sh
git clone -b Simulation_Control https://github.com/Anocim/ClawDrone.git
cd ClawDrone/px4-f550-gz
```

### 3. Install the simulation files

```sh
./install.sh --list                                          # variants, targets and worlds
./install.sh --px4 ~/PX4-Autopilot                           # every variant (default)
./install.sh --px4 ~/PX4-Autopilot --variant f550            # one variant (+ its requires)
./install.sh --px4 ~/PX4-Autopilot --variant f550_simple
./install.sh --px4 ~/PX4-Autopilot --variant f550_patas
```

Use the **folder name** after `--variant`. `f550` is the detailed model;
there is no `f550_detailed` folder.

| Option | Description |
|---|---|
| `--px4 <path>` | PX4-Autopilot directory (default `~/PX4-Autopilot`) |
| `--variant <name>` | Install one variant instead of all. Its `requires` dependencies are installed too |
| `--list` | List variants, make targets and worlds |
| `--no-meshes` | Skip the bundled 3D meshes |
| `--uninstall` | Revert the installation (meshes and worlds are removed only with `--variant all`) |
| `--keep-cache` | Do not delete `build/px4_sitl_default/CMakeCache.txt` |
| `--help` | Full documentation of the script |

For every selected variant the script:

1. refuses to continue if the numeric airframe ID **or the make target** is already provided by a different airframe;
2. copies its `models/*` to `PX4-Autopilot/Tools/simulation/gz/models/`;
3. copies its `airframe/*` to `PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/`;
4. adds each airframe name to that folder's `CMakeLists.txt` (right after `4001_gz_x500`), which creates the `gz_<name>` make target.

It also, once per run:

5. removes leftovers that break the launch: the legacy airframe `4051_gz_f550` and any `*_gz_*` airframe in `build/px4_sitl_default/etc/init.d-posix/airframes/` that no longer exists in ROMFS (see [Troubleshooting](#troubleshooting));
6. copies the bundled meshes to `Tools/simulation/gz/models/mrs_robots_description/` (only if a selected variant uses them);
7. copies `worlds/*.sdf` to `Tools/simulation/gz/worlds/` and registers the world if this PX4 version needs it;
8. deletes `parameters*.bson` and `dataman` from `build/px4_sitl_default/rootfs/`, so PX4 starts clean (a value once saved with `param set` + `param save` would otherwise win over the airframe default);
9. deletes `build/px4_sitl_default/CMakeCache.txt` unless `--keep-cache` was given, so the new make targets are generated.

It is idempotent and only touches files inside the PX4 checkout.

### 4. ROS 2 and DDS side

The ROS 2 workspace and its dependencies are documented in
[`f550_ws/README.md`](../f550_ws/README.md) and
[`f550_ws/INSTALL.md`](../f550_ws/INSTALL.md). The Micro XRCE-DDS Agent is a
runtime dependency built **outside** this repository; use `v2.4.2` with the
Fast-DDS workaround described in
[`f550_ws/README.md`](../f550_ws/README.md#micro-xrce-dds-agent-external-dependency).
PX4 SITL starts its uXRCE-DDS client automatically and connects to the agent
on UDP port `8888`.

## Running the simulation

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550                  # detailed model
make px4_sitl gz_f550_simple           # simple model
make px4_sitl gz_f550_patas            # model with landing legs
make px4_sitl gz_f550_detailed_mono_cam_down
PX4_GZ_WORLD=tenis make px4_sitl gz_f550   # tennis world
```

The first build recompiles because `CMakeLists.txt` changed. If `make` reports
that the target does not exist:

```sh
rm -f build/px4_sitl_default/CMakeCache.txt && make px4_sitl gz_f550
```

Switching between variants needs no manual cleanup: PX4 detects the new
`SYS_AUTOSTART` (for example `SYS_AUTOSTART: curr: 4050 -> new: 4051` in the
startup log) and resets its parameters to the new airframe's defaults.

In the PX4 shell (`pxh>`), for manual flying:

```sh
commander arm
commander takeoff
```

### Manual installation (equivalent to the script)

```sh
cd ~/PX4-Autopilot
R=~/ClawDrone/px4-f550-gz
cp -r $R/variants/f550/models/*                          Tools/simulation/gz/models/
cp -r $R/variants/f550_simple/models/*                   Tools/simulation/gz/models/
cp -r $R/variants/f550_patas/models/*                    Tools/simulation/gz/models/
cp -r $R/variants/*_mono_cam_down/models/*               Tools/simulation/gz/models/
cp -r $R/third_party/mrs_robots_description              Tools/simulation/gz/models/
cp -r $R/worlds/*.sdf                                    Tools/simulation/gz/worlds/
cp $R/variants/f550/airframe/*                           ROMFS/px4fmu_common/init.d-posix/airframes/
cp $R/variants/f550_simple/airframe/*                    ROMFS/px4fmu_common/init.d-posix/airframes/
cp $R/variants/f550_patas/airframe/*                     ROMFS/px4fmu_common/init.d-posix/airframes/
cp $R/variants/*_mono_cam_down/airframe/*                ROMFS/px4fmu_common/init.d-posix/airframes/
rm -f build/px4_sitl_default/rootfs/parameters*.bson build/px4_sitl_default/rootfs/dataman
```

Then add all airframe names to
`ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt`:

```cmake
	4001_gz_x500
	4050_gz_f550
	4051_gz_f550_simple
	4052_gz_f550_patas
	4053_gz_f550_detailed_mono_cam_down
	4054_gz_f550_simple_mono_cam_down
	4055_gz_f550_patas_mono_cam_down
```

The camera variants also need the `mono_cam` model from PX4's Gazebo model
directory; this repository does not bundle it.

## 3D meshes

`f550` uses five `.dae` meshes from the CTU MRS group, bundled in
`third_party/mrs_robots_description/` with their BSD-3-Clause license. The
installer copies them automatically (skip with `--no-meshes`). They only affect
how the drone looks, never the physics. `f550_patas` ships its own meshes and
does not use `third_party/`. `f550_simple` uses no meshes. Keep every mesh
folder together with its `LICENSE`.

## Verification

In `pxh>` right after launching:

| Variant | Command | Expected |
|---|---|---|
| `f550` | `param show CA_ROTOR0_PY` | `0.275` |
| `f550` | `param show CA_ROTOR4_KM` | `-0.06` |
| `f550_simple` | `param show CA_ROTOR0_PY` | `0.1375` |
| `f550_simple` | `param show CA_ROTOR4_KM` | `0.05` |
| `f550_patas` | `param show CA_ROTOR0_PY` | `0.275` |
| `f550_patas` | `param show CA_ROTOR0_KM` | `-0.06` |

Camera variants inherit the parameters of their base variant. Other values
mean PX4 still reads an old airframe or saved parameters: rerun `install.sh`
and rebuild.

**Motor mapping test** (vehicle disarmed): in the Gazebo GUI enable "Transform
control" and select the model (red axis = X = front, green axis = Y = left),
then run `actuator_test set -f 101 -v 0.4 -t 3` and repeat with 102 ... 106.
The rotor that spins must be:

| Function | `f550` | `f550_simple` |
|---|---|---|
| 101 | `prop_0`: on the X axis, -Y side | `rotor_0`: +X, -Y |
| 102 | `prop_1`: on the X axis, +Y side | `rotor_1`: on the X axis, -Y side |
| 103 | `prop_2`: +X, +Y | `rotor_2`: -X, -Y |
| 104 | `prop_3`: -X, -Y | `rotor_3`: -X, +Y |
| 105 | `prop_4`: +X, -Y | `rotor_4`: on the X axis, +Y side |
| 106 | `prop_5`: -X, +Y | `rotor_5`: +X, +Y |

**Gazebo camera topics** (with a `*_mono_cam_down` variant): find the exact
name with `gz topic -l | grep image`. `f550_vision` bridges them to ROS 2; see
[its README](../f550_ws/src/f550_vision/README.md).

## Troubleshooting

| Symptom | Possible cause | Suggested action |
|---|---|---|
| `gz_f550` fails (unknown model, ambiguous or wrong `SYS_AUTOSTART`) but `gz_f550_simple` works | A leftover airframe `4051_gz_f550` (old name of the simple variant) makes the target `gz_f550` match two airframes | Rerun `./install.sh` (it removes it), then `make px4_sitl gz_f550`. Check below |
| `make ... gz_<name>` target not found | Airframe not registered in `CMakeLists.txt`, or stale CMake cache | Rerun `install.sh`, delete `build/px4_sitl_default/CMakeCache.txt`, rebuild |
| `install.sh` says the make target or ID "would be ambiguous" | Another airframe in PX4 already provides it | Remove that airframe or rename the one in the variant |
| `install.sh` reports an unknown variant | `--variant` expects the folder name, not the model nickname | Use `f550` instead of `f550_detailed`; run `--list` |
| `param show` returns old values | Stale airframe in `build/` or a value saved from the PX4 shell | Rerun `install.sh` (cleans both), rebuild |
| Drone flips on takeoff, or `actuator_motors` is saturated (e.g. `[1, 0.5, 0, 0, 0.5, 1]`) | `CA_ROTORn_*` do not match the SDF | Regenerate with [`tools/gen_ca.py`](tools/README.md) |
| Mesh warnings, or Gazebo GUI crashes with the detailed model | Meshes not installed, or GPU/driver problem rendering them | Rerun without `--no-meshes`; try `HEADLESS=1 make px4_sitl gz_f550` or `PX4_GZ_SIM_RENDER_ENGINE=ogre make px4_sitl gz_f550` |
| The wrong or an old model appears | An older copy of `f550` earlier in `GZ_SIM_RESOURCE_PATH` | `echo $GZ_SIM_RESOURCE_PATH`; remove stale paths from `~/.bashrc` |
| `f550_simple` shows the detailed body | `f550_simple/model.sdf` includes `model://f550_base` | It must include `model://f550_base_simple` |
| A camera variant does not start | The `mono_cam` model is missing from PX4's Gazebo model path | Verify `model://mono_cam` resolves in the PX4 checkout |
| The tennis world does not load | World not copied or PX4 did not register it | Rerun `install.sh`; see [`worlds/README.md`](worlds/README.md) |
| Standard `gz_x500` simulation fails | PX4 or Gazebo setup problem | Verify the PX4 installation before debugging this repository |

**Check for leftover airframes** (exactly the six current IDs must appear in
both lists):

```sh
ls ~/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes | grep f550
ls ~/PX4-Autopilot/build/px4_sitl_default/etc/init.d-posix/airframes | grep f550
```

**Get the real error** when a variant does not start:

```sh
GZ_VERBOSE=4 make px4_sitl gz_f550 2>&1 | tee /tmp/f550.log
```

## Adding a new variant

Create `variants/<name>/` from [`_template/`](variants/_template/README.md).
`install.sh` discovers any folder in `variants/` (not starting with `_`) that
has at least one file in `airframe/`; the script never needs editing. Each
variant needs its own Gazebo model folders, PX4 airframe, a unique airframe ID
and a unique make target (the part of the airframe file name after the ID,
e.g. `4051_gz_f550_simple` gives `gz_f550_simple`). If the new model extends an
existing one, add a `requires` file listing the base variant folder name, one
per line, as the `*_mono_cam_down` variants do. Add a short README following
the existing variant files.
