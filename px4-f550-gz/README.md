# px4-f550-gz

DJI F550 hexacopter models for **PX4 SITL + Gazebo (gz-sim)**, with ready-to-use PX4 airframes and an
installer that puts everything in the right place inside a fresh PX4-Autopilot checkout.

> **Tested with:** PX4-Autopilot `<commit/tag>` | Gazebo `<Harmonic/other>` | Ubuntu `<version>`
> (fill in with `git -C ~/PX4-Autopilot describe --tags` and `gz sim --version`).

## Repository layout

```
px4-f550-gz/
|-- install.sh                    # installer (fully commented: read its header to see every step)
|-- tools/gen_ca.py               # generates CA_ROTORn parameters from an SDF model
|-- variants/                     # one folder per simulation model
|   |-- f550_detailed/            #   detailed model (sensors, per-motor plugins, meshes)
|   |   |-- airframe/             #     PX4 airframe file(s)      -> PX4-Autopilot/ROMFS/.../airframes/
|   |   |-- models/               #     Gazebo model folders      -> PX4-Autopilot/Tools/simulation/gz/models/
|   |   `-- README.md             #     motor layout and parameters
|   |-- f550_simple/              #   simple model: EMPTY PLACEHOLDER for now
|   `-- _template/                #   how to create a variant (ignored by install.sh)
`-- third_party/
    `-- mrs_robots_description/   # bundled 3D meshes (BSD-3-Clause, CTU MRS) + their LICENSE
```

## Variants

| Variant | PX4 airframe | Make target | Description |
|---|---|---|---|
| `f550_detailed` | `4050_gz_f550` | `make px4_sitl gz_f550` | IMU, magnetometer, barometer, GPS, one motor plugin per propeller, meshes |
| `f550_simple` | *(not yet)* | *(not yet)* | Placeholder folder; skipped by the installer until it has an airframe |

`./install.sh --list` always shows the current state.

## Install (for someone who just cloned PX4)

### 1. PX4 prerequisites

```sh
git clone --recursive https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot
cd ~/PX4-Autopilot
bash ./Tools/setup/ubuntu.sh        # installs dependencies and Gazebo; log out/in if asked
make px4_sitl gz_x500               # sanity check: the stock simulator must work first
```

If `gz_x500` does not start, the problem is the PX4/Gazebo installation, not this repository.

### 2. Install the models

```sh
git clone https://github.com/<your_user>/px4-f550-gz.git ~/px4-f550-gz
cd ~/px4-f550-gz
./install.sh --px4 ~/PX4-Autopilot                           # every installable variant
./install.sh --px4 ~/PX4-Autopilot --variant f550_detailed   # only one
```

Options: `--no-meshes` (skip the bundled meshes), `--uninstall` (revert), `--list`, `--help`.
`--px4` defaults to `~/PX4-Autopilot`.

For every selected variant the script:

1. checks that the numeric airframe ID is not used by a *different* airframe (refuses to continue otherwise);
2. copies its `models/*` to `PX4-Autopilot/Tools/simulation/gz/models/`;
3. copies its `airframe/*` to `PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes/`;
4. adds each airframe name to that folder's `CMakeLists.txt` (one line, right after `4001_gz_x500`),
   which is what creates the `gz_<name>` make target.

Then, once:

5. copies the bundled meshes to `Tools/simulation/gz/models/mrs_robots_description/`;
6. deletes `parameters*.bson` and `dataman` in `build/px4_sitl_default/rootfs/`, because PX4 would
   otherwise keep the parameters saved by an earlier run and ignore the new airframe.

It is idempotent (safe to run repeatedly) and only touches files inside the PX4 checkout.

### 3. Run

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550
```

In the `pxh>` console:

```sh
commander arm
commander takeoff
```

The first build recompiles because `CMakeLists.txt` changed. If `make` says the target does not exist:

```sh
rm -f build/px4_sitl_default/CMakeCache.txt && make px4_sitl gz_f550
```

### Manual install (equivalent to the script)

```sh
cd ~/PX4-Autopilot
cp -r ~/px4-f550-gz/variants/f550_detailed/models/*  Tools/simulation/gz/models/
cp -r ~/px4-f550-gz/third_party/mrs_robots_description Tools/simulation/gz/models/
cp ~/px4-f550-gz/variants/f550_detailed/airframe/*   ROMFS/px4fmu_common/init.d-posix/airframes/
rm -f build/px4_sitl_default/rootfs/parameters*.bson build/px4_sitl_default/rootfs/dataman
```

and add the airframe name to `ROMFS/px4fmu_common/init.d-posix/airframes/CMakeLists.txt`:

```cmake
	4001_gz_x500
	4050_gz_f550
```

## 3D meshes

The visuals use five `.dae` meshes from the CTU MRS group, **bundled** in `third_party/mrs_robots_description/`
together with their BSD-3-Clause license, so nobody has to download anything. The installer copies them
automatically. They only affect how the drone looks, never the physics. Upstream source, copied commit and file
list are in `third_party/mrs_robots_description/README.md`. Keep that folder together with its `LICENSE`.

## Verification

In `pxh>` (values for `f550_detailed`):

```sh
param show CA_ROTOR0_PY    # -> 0.275
param show CA_ROTOR4_KM    # -> -0.06
```

Other values mean PX4 still reads an old airframe or saved parameters: rerun `install.sh` and rebuild.

Motor mapping test (vehicle **disarmed**): in the Gazebo GUI enable "Transform control" and select the model
(red axis = X = front, green axis = Y = left), then:

```sh
actuator_test set -f 101 -v 0.4 -t 3     # repeat with 102 ... 106
```

The propeller that spins must match the table in `variants/f550_detailed/README.md`. In hover,
`listener actuator_motors` should show six similar values (about 0.5), not saturated outputs.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Flips on takeoff, or `actuator_motors` saturated (e.g. `[1, .5, 0, 0, .5, 1]`) | `CA_ROTORn_*` do not match the SDF | Regenerate with `tools/gen_ca.py` (see the variant README) |
| Spins about yaw | Wrong `KM` sign or `turningDirection` on some motor | Check rule 3 in the variant README |
| `make ... gz_f550` target not found | Airframe not registered in `CMakeLists.txt` | Rerun `install.sh`, delete `CMakeCache.txt` |
| `param show` returns old values | Saved parameters or stale build | Rerun `install.sh`, rebuild |
| Airframe ID already in use | Another airframe has that numeric prefix | Rename the airframe file in the variant |
| "mesh not found" warnings | Installed with `--no-meshes`, or meshes folder missing | Rerun `install.sh` without `--no-meshes` |

## Adding a variant

Copy `variants/_template/` to `variants/<name>/` (or fill in the `f550_simple` placeholder) and follow the
template README. `install.sh` discovers any folder in `variants/` (not starting with `_`) that has at least one
file in `airframe/`; the script never needs editing. Use a unique airframe ID, a unique `PX4_SIM_MODEL`, and
model folder names that do not clash with other variants.

## Branching

`main` is the only long-lived branch. Work on short-lived branches (`feature/...`, `fix/...`) merged through pull
requests. New kinds of material (for example ROS 2 or hardware) are added later as new top-level folders on `main`,
not as parallel branches, so shared geometry is fixed once. Create a compatibility branch or tag (`px4-v1.16`, ...)
only if a PX4 release breaks `main`.

## Credits and license

Based on the DJI F550 description from the MRS group (CTU in Prague); meshes are redistributed under their
BSD-3-Clause license (see `third_party/mrs_robots_description/LICENSE`). Add your own `LICENSE` for the rest of this repository.
