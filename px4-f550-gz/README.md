# px4-f550-gz

DJI F550 hexacopter simulation models for **PX4 SITL + Gazebo Sim**: two model variants, their PX4 airframes and an
installer that integrates them into a PX4-Autopilot checkout.

> **Tested with:**
> - Ubuntu 22.04.5 LTS
> - PX4-Autopilot `v1.18.0-beta1-1084-g95ede794c0`
> - Gazebo Sim 8.10.0
> - ROS 2 Humble (installed in the development environment)

This folder lives on the `Simulation_Control` branch of the ClawDrone repository.

## Variants and make targets

Each variant has **its own airframe and its own make target**, so both can be installed together and chosen at launch time.

| Variant | PX4 airframe | Make target | Description |
|---|---|---|---|
| `f550_detailed` | `4050_gz_f550` | `make px4_sitl gz_f550` | Detailed model: 3D meshes, 2.0 kg, sensors, one motor plugin per propeller |
| `f550_simple` | `4051_gz_f550_simple` | `make px4_sitl gz_f550_simple` | Simple model: primitive shapes, 1.5 kg, same sensors |

| | `f550_detailed` | `f550_simple` |
|---|---|---|
| Visuals | CTU-MRS meshes (bundled in `third_party/`) | Boxes and cylinders |
| Mass | 2.03 kg | 1.596 kg |
| `motorConstant` / `maxRotVelocity` | 1.05e-5 / 1100 rad/s | 5.2e-6 / 1000 rad/s |
| Thrust-to-weight | about 3.8 | about 2.0 |
| `KM` | +/-0.06 | +/-0.05 |
| Motor 0 is the... | right rotor | front-right rotor |

Motor layout, tables and parameters of each variant: `variants/<name>/README.md`.
`./install.sh --list` shows the variants and their make targets.

## Repository layout

```text
px4-f550-gz/
|-- install.sh                    # Installer (fully commented: read its header)
|-- tools/
|   `-- gen_ca.py                 # Generates control allocation parameters from an SDF
|-- variants/
|   |-- f550_detailed/            # Detailed F550 model
|   |   |-- airframe/4050_gz_f550
|   |   |-- models/{f550, f550_base}/
|   |   `-- README.md
|   |-- f550_simple/              # Simplified F550 model
|   |   |-- airframe/4051_gz_f550_simple
|   |   |-- models/{f550_simple, f550_base_simple}/
|   |   `-- README.md
|   `-- _template/                # Template for creating new variants
`-- third_party/
    `-- mrs_robots_description/   # Bundled 3D meshes (BSD-3-Clause) and their license
```

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

If the standard simulation does not launch, check the PX4 and Gazebo installation first.

### 2. Clone this repository

```sh
git clone -b Simulation_Control https://github.com/Anocim/ClawDrone.git
cd ClawDrone/px4-f550-gz
```

### 3. Install

```sh
./install.sh --list                                           # variants and make targets
./install.sh --px4 ~/PX4-Autopilot                            # every variant (default)
./install.sh --px4 ~/PX4-Autopilot --variant f550_detailed    # only one
./install.sh --px4 ~/PX4-Autopilot --variant f550_simple
```

| Option | Description |
|---|---|
| `--px4 <path>` | PX4-Autopilot directory (default `~/PX4-Autopilot`) |
| `--variant <name>` | Install one variant instead of all |
| `--list` | List variants and their make targets |
| `--no-meshes` | Skip the bundled 3D meshes |
| `--uninstall` | Revert the installation |
| `--help` | Full documentation of the script |

For every selected variant the script:

1. refuses to continue if the numeric airframe ID **or the make target** is already provided by a different airframe;
2. copies its `models/*` to `PX4-Autopilot/Tools/simulation/gz/models/`;
3. copies its `airframe/*` to `PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/`;
4. adds each airframe name to that folder's `CMakeLists.txt` (right after `4001_gz_x500`), which creates the `gz_<name>` make target.

It also, once per run:

5. removes leftovers that break the launch: the legacy airframe `4051_gz_f550` (the old name of the simple variant)
   and any `*_gz_*` airframe in `build/px4_sitl_default/etc/init.d-posix/airframes/` that no longer exists in ROMFS
   (see [Troubleshooting](#troubleshooting));
6. copies the bundled meshes to `Tools/simulation/gz/models/mrs_robots_description/` (only if a selected variant uses them);
7. deletes `parameters*.bson` and `dataman` from `build/px4_sitl_default/rootfs/`, so PX4 starts clean (a value you once saved with `param set` + `param save` would otherwise win over the airframe default).

It is idempotent and only touches files inside the PX4 checkout.

## Running the simulation

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550             # detailed model
make px4_sitl gz_f550_simple      # simple model
```

The first build recompiles because `CMakeLists.txt` changed. If `make` reports that the target does not exist:

```sh
rm -f build/px4_sitl_default/CMakeCache.txt && make px4_sitl gz_f550
```

Switching between variants needs no manual cleanup: PX4 detects the new `SYS_AUTOSTART` (for example
`SYS_AUTOSTART: curr: 4050 -> new: 4051` in the startup log) and resets its parameters to the new airframe's defaults.

In the PX4 shell (`pxh>`):

```sh
commander arm
commander takeoff
```

### Manual installation (equivalent to the script)

```sh
cd ~/PX4-Autopilot
R=~/ClawDrone/px4-f550-gz
cp -r $R/variants/f550_detailed/models/*  Tools/simulation/gz/models/
cp -r $R/variants/f550_simple/models/*    Tools/simulation/gz/models/
cp -r $R/third_party/mrs_robots_description Tools/simulation/gz/models/
cp $R/variants/f550_detailed/airframe/*   ROMFS/px4fmu_common/init.d-posix/airframes/
cp $R/variants/f550_simple/airframe/*     ROMFS/px4fmu_common/init.d-posix/airframes/
rm -f build/px4_sitl_default/rootfs/parameters*.bson build/px4_sitl_default/rootfs/dataman
```

Then add both airframe names to `ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt`:

```cmake
	4001_gz_x500
	4050_gz_f550
	4051_gz_f550_simple
```

## 3D meshes

`f550_detailed` uses five `.dae` meshes from the CTU MRS group, bundled in `third_party/mrs_robots_description/`
with their BSD-3-Clause license. The installer copies them automatically (skip with `--no-meshes`). They only affect
how the drone looks, never the physics. `f550_simple` does not use them. Keep the folder together with its `LICENSE`.

## Verification

In `pxh>` right after launching:

| Variant | Command | Expected |
|---|---|---|
| `f550_detailed` | `param show CA_ROTOR0_PY` | `0.275` |
| `f550_detailed` | `param show CA_ROTOR4_KM` | `-0.06` |
| `f550_simple` | `param show CA_ROTOR0_PY` | `0.1375` |
| `f550_simple` | `param show CA_ROTOR4_KM` | `0.05` |

Other values mean PX4 still reads an old airframe or saved parameters: rerun `install.sh` and rebuild.

**Motor mapping test** (vehicle disarmed): in the Gazebo GUI enable "Transform control" and select the model
(red axis = X = front, green axis = Y = left), then run `actuator_test set -f 101 -v 0.4 -t 3` and repeat with
102 ... 106. The rotor that spins must be:

| Function | `f550_detailed` | `f550_simple` |
|---|---|---|
| 101 | `prop_0`: on the X axis, -Y side | `rotor_0`: +X, -Y |
| 102 | `prop_1`: on the X axis, +Y side | `rotor_1`: on the X axis, -Y side |
| 103 | `prop_2`: +X, +Y | `rotor_2`: -X, -Y |
| 104 | `prop_3`: -X, -Y | `rotor_3`: -X, +Y |
| 105 | `prop_4`: +X, -Y | `rotor_4`: on the X axis, +Y side |
| 106 | `prop_5`: -X, +Y | `rotor_5`: +X, +Y |

## Troubleshooting

| Symptom | Possible cause | Suggested action |
|---|---|---|
| `gz_f550` fails (unknown model, ambiguous or wrong `SYS_AUTOSTART`) but `gz_f550_simple` works | A leftover airframe `4051_gz_f550` (old name of the simple variant) makes the target `gz_f550` match two airframes | Rerun `./install.sh` (it removes it), then `make px4_sitl gz_f550`. Check below |
| `make ... gz_f550` target not found | Airframe not registered in `CMakeLists.txt` | Rerun `install.sh`, delete `build/px4_sitl_default/CMakeCache.txt`, rebuild |
| `install.sh` says the make target or ID "would be ambiguous" | Another airframe in PX4 already provides it | Remove that airframe or rename the one in the variant |
| `param show` returns old values | Stale airframe in `build/` or a value saved from the PX4 shell | Rerun `install.sh` (cleans both), rebuild |
| Drone flips on takeoff, or `actuator_motors` is saturated (e.g. `[1, 0.5, 0, 0, 0.5, 1]`) | `CA_ROTORn_*` do not match the SDF | Regenerate with `tools/gen_ca.py` (see the variant README) |
| Mesh warnings, or Gazebo GUI crashes with the detailed model | Meshes not installed, or GPU/driver problem rendering them | Rerun without `--no-meshes`; try `HEADLESS=1 make px4_sitl gz_f550` (no GUI) or `PX4_GZ_SIM_RENDER_ENGINE=ogre make px4_sitl gz_f550` |
| The wrong or an old model appears | An older copy of `f550` earlier in `GZ_SIM_RESOURCE_PATH` | `echo $GZ_SIM_RESOURCE_PATH`; remove stale paths from `~/.bashrc` |
| `f550_simple` shows the detailed body | `f550_simple/model.sdf` includes `model://f550_base` | It must include `model://f550_base_simple` |
| Standard `gz_x500` simulation fails | PX4 or Gazebo setup problem | Verify the PX4 installation before debugging this repository |

**Check for leftover airframes** (exactly `4050_gz_f550` and `4051_gz_f550_simple` must appear in both lists):

```sh
ls ~/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes | grep f550
ls ~/PX4-Autopilot/build/px4_sitl_default/etc/init.d-posix/airframes | grep f550
```

**Get the real error** when a variant does not start:

```sh
GZ_VERBOSE=4 make px4_sitl gz_f550 2>&1 | tee /tmp/f550.log
```

## Adding a new variant

Create `variants/<name>/` from `_template/`. `install.sh` discovers any folder in `variants/` (not starting with `_`)
that has at least one file in `airframe/`; the script never needs editing. Each variant needs its own Gazebo model
folders, PX4 airframe, a unique airframe ID and a unique make target (the part of the airframe file name after the ID,
e.g. `4051_gz_f550_simple` gives `gz_f550_simple`).

## Development status

The current development environment supports PX4 SITL, Gazebo Sim 8, the detailed and simplified DJI F550 models
and a ROS 2 Humble installation. Further work will focus on developing and testing the vehicle control system within
this simulation setup.

## References

- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
- [PX4 Gazebo Simulation](https://docs.px4.io/main/en/sim_gazebo_gz/)
- [Gazebo Sim](https://gazebosim.org/docs)
- [ROS 2 Humble](https://docs.ros.org/en/humble/)

## License and credits

The bundled MRS mesh resources are distributed under their BSD-3-Clause license, included in
`third_party/mrs_robots_description/`. Based on the DJI F550 description from the MRS group (CTU in Prague).
Refer to the license files before redistributing third-party resources.
