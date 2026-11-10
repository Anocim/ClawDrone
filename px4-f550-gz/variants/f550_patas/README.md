# f550_patas

DJI Flame Wheel F550 hexacopter model for PX4 SITL and Gazebo Harmonic, with six motors and three
landing legs. PX4 airframe `4052_gz_f550_patas`, run with `make px4_sitl gz_f550_patas`.

This variant preserves the physical model and control configuration copied from the working local
PX4 model `Tools/simulation/gz/models/f550/` and airframe `22001_gz_f550`. Its separate model name,
mesh URI namespace and airframe target allow installation without replacing that original model.
The copied motor housing mesh has one XML repair: `MOTOR Motor&Proplr` is escaped as
`MOTOR Motor&amp;Proplr` in its attribute. No physical or control parameters were changed.

**Flight-test status:** the owner reports completed flight tests of the original model and airframe.
The renamed `f550_patas` variant has not yet been flight-tested. Static validation of these files
does not establish flight stability, successful rendering or runtime compatibility.

## Directory layout

```text
f550_patas/
|-- README.md
|-- airframe/
|   `-- 4052_gz_f550_patas
`-- models/
    `-- f550_patas/
        |-- model.config
        |-- model.sdf
        |-- LICENSE_MRS
        `-- meshes/
            |-- dji_f550_arm.dae
            |-- dji_f550_central_board.dae
            |-- dji_f550_leg_170mm.dae
            |-- dji_f550_prop.dae
            `-- dji_f550_rotor.dae
```

| Path | Installed into `PX4-Autopilot/` | Purpose |
|---|---|---|
| `airframe/4052_gz_f550_patas` | `ROMFS/px4fmu_common/init.d-posix/airframes/` | Rotor geometry and six motor outputs |
| `models/f550_patas/` | `Tools/simulation/gz/models/f550_patas/` | Self-contained SDF, meshes and license |

All mesh references use `model://f550_patas/meshes/`. No base-model include or shared
`mrs_robots_description` installation is required for this variant.

## Physical parameters

Values below come from `model.sdf` and the airframe, rather than hardware specifications.

| Property | Value |
|---|---|
| SDF version | 1.9 |
| Base-link mass | 2.0 kg |
| Rotor-link mass | 0.005 kg each; total model mass 2.03 kg |
| Base inertia `(Ixx, Iyy, Izz)` | `(0.0316666666667, 0.0316666666667, 0.0625)` kg m²; cross terms zero |
| Rotor inertia `(Ixx, Iyy, Izz)` | `(1.74066666667e-5, 1.74066666667e-5, 3.481e-5)` kg m²; cross terms zero |
| Rotor radius from model origin | Approximately 0.275 m |
| SDF model pose | `(0, 0, 0.25, 0, 0, 0)`; no airframe spawn-pose override |
| Body collision | Cylinder, radius 0.11 m, length 0.07 m, center z = -0.015 m |
| Sensors | IMU 250 Hz, magnetometer 100 Hz, air pressure 50 Hz, navsat 30 Hz |

The model is dynamic, gravity is enabled and model self-collision is disabled. The legs are visuals
and collisions on `base_link`; they have no separate mass or inertia entries.

### Landing legs

Three `dji_f550_leg_170mm.dae` visuals use scale `(0.001, 0.001, 0.001)` and center z = -0.110 m.
Each has a vertical cylinder collision with radius **0.012 m**, length **0.17 m** and center
z = **-0.143 m**. Coordinates are in the base-link frame (Gazebo FLU):

| Leg | x (m) | y (m) | Visual yaw (rad) |
|---|---:|---:|---:|
| 0 | +0.23192160 | -0.13390000 | +2.6179938780 |
| 1 | 0 | +0.26780000 | -1.5707963268 |
| 2 | -0.23192160 | -0.13390000 | +0.5235987756 |

The cylinders approximate contact geometry; they do not reproduce the detailed mesh shape.

## Motor layout and control

Gazebo uses FLU coordinates (+X front, +Y left, +Z up); PX4 rotor positions use FRD
(+X front, +Y right, +Z down). Thus PX4 `PY = -y` and `PZ = -z` from the SDF.
Directions below are viewed from above. Every rotor has SDF z = +0.0115 m and PX4 `PZ = -0.0115 m`.

| Motor / `motorNumber` | Function | Position | PX4 `PX` (m) | PX4 `PY` (m) | Spin | `KM` |
|---|---|---|---:|---:|---|---:|
| 0 | 101 | Right | 0 | +0.275 | CW | -0.06 |
| 1 | 102 | Left | 0 | -0.275 | CCW | +0.06 |
| 2 | 103 | Front left | +0.23816 | -0.1375 | CW | -0.06 |
| 3 | 104 | Back right | -0.23816 | +0.1375 | CCW | +0.06 |
| 4 | 105 | Front right | +0.23816 | +0.1375 | CCW | +0.06 |
| 5 | 106 | Back left | -0.23816 | -0.1375 | CW | -0.06 |

Each `rotor_n` link has a `rotor_n_joint` and a `gz::sim::systems::MulticopterMotorModel` plugin.
The six plugins share these settings:

| Parameter | Value |
|---|---|
| `motorConstant` | 1.05e-5 |
| `momentConstant` | 0.06 |
| `maxRotVelocity` | 1100 rad/s |
| `timeConstantUp` / `timeConstantDown` | 0.0125 / 0.025 s |
| `rotorDragCoefficient` | 1.0e-4 |
| `rollingMomentCoefficient` | 1.0e-6 |
| `rotorVelocitySlowdownSim` | 15 |
| `motorType` / `commandSubTopic` | `velocity` / `command/motor_speed` |
| PX4 `SIM_GZ_EC_MIN1..6` / `MAX1..6` | 150 / 1000 rad/s |

The airframe sets `SIM_GZ_EN=1`, `MAV_TYPE=13`, `CA_AIRFRAME=0`, `CA_ROTOR_COUNT=6` and
`CA_ROTORn_CT=1.0`. It sources `rc.mc_defaults` and does not explicitly set `MPC_THR_HOVER`.
Keep the motor indices, positions, directions and `KM` signs together when reviewing the configuration.

## Requirements

- A PX4-Autopilot checkout with SITL build dependencies, Gazebo integration and initialized simulation
  submodules. Static review used local PX4 `v1.18.0-beta1-1230-g989a01382b`; this is not a runtime
  compatibility certification or a minimum supported version.
- Gazebo Harmonic with SDF 1.9 support, the `gz-sim-multicopter-motor-model-system` plugin and the
  sensor systems required by the PX4 Gazebo world. Runtime loading remains to be checked.
- Bash and the standard tools used by `install.sh`, including GNU `find`, `cp`, `grep`, `awk` and `sed`.
- Python 3 with the standard-library XML parser for the optional static checks below.

The five visual meshes are bundled. No ROS installation or additional mesh download is required
by this self-contained model. An existing working PX4/Gazebo installation is assumed here.

## Installation and launch

**Back up saved SITL state before installation, or use an isolated PX4 checkout.** The current
`install.sh` unconditionally deletes `build/px4_sitl_default/rootfs/parameters*.bson` and `dataman`,
including when only this variant is selected or uninstalled. These files belong to the shared SITL
rootfs. Installing the model also writes an airframe and updates PX4's airframe `CMakeLists.txt`.

From `ClawDrone/px4-f550-gz/`, inspect the variants and install only this one:

```sh
./install.sh --list
./install.sh --px4 ~/PX4-Autopilot --variant f550_patas
```

Replace `--px4` with the path to an isolated checkout when preserving a working installation.
The script discovers this variant automatically and copies its local meshes and license.

**Use `--variant f550_patas`, not the default all-variants installation.** The existing detailed and
simple airframes share the `gz_f550` target with the original `22001_gz_f550`; detailed also installs
over the original `models/f550/`. Those conflicts are outside this variant's scope. Patas uses its
own ID `4052`, target and model directory. Check that the destination has no unrelated files using
that ID, target or directory; the installer only checks conflicting numeric airframe IDs.

After installation, launch from the selected PX4 checkout:

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550_patas
```

Use the same isolated checkout path here if one was selected above. Existing conflicting airframes
already installed in that checkout can still prevent CMake from generating targets.

## Validation

### Static checks (no simulator required)

Run from `ClawDrone/px4-f550-gz/`:

```sh
python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

model = Path('variants/f550_patas/models/f550_patas')
for path in [model / 'model.config', model / 'model.sdf', *sorted((model / 'meshes').glob('*.dae'))]:
    ET.parse(path)
    print('XML OK:', path)

config = ET.parse(model / 'model.config').getroot()
sdf = ET.parse(model / 'model.sdf').getroot()
assert config.findtext('name') == sdf.find('model').get('name') == model.name
assert config.find('sdf').get('version') == sdf.get('version') == '1.9'
assert config.findtext('sdf') == 'model.sdf'
for uri in sdf.iter('uri'):
    prefix = 'model://f550_patas/'
    assert uri.text.startswith(prefix), uri.text
    assert (model / uri.text[len(prefix):]).is_file(), uri.text
print('Model names and mesh references OK')
PY
sh -n variants/f550_patas/airframe/4052_gz_f550_patas
bash -n install.sh
./install.sh --list
```

XML parsing checks well-formedness, not full SDF or COLLADA schema compliance. The list command
should include `f550_patas -> make px4_sitl gz_f550_patas`. Also review the motor table against the
airframe and SDF before runtime testing.

### Runtime checks (pending; simulation only)

These procedures are for a later test session and have not been executed for this renamed variant:

1. Confirm that the installed target starts without missing meshes, plugins or sensors. Inspect all
   three landing legs and ground contact before arming.
2. In the PX4 console, inspect `CA_ROTOR_COUNT`, `CA_ROTOR0_PY`, `CA_ROTOR0_KM` and
   `SIM_GZ_EC_FUNC1` with `param show`; expect `6`, `0.275`, `-0.06` and `101`, respectively.
   Check the other motors against the table. Saved parameters or environment overrides can change
   the effective configuration.
3. With the simulated vehicle disarmed, verify the motor mapping one output at a time:

   ```sh
   actuator_test set -f 101 -v 0.4 -t 3
   ```

   Repeat for functions 102 through 106. Confirm the expected rotor and direction before flight.
4. Only after those checks, perform a controlled simulated takeoff, hover and landing. Inspect motor
   outputs with `listener actuator_motors` for saturation or strong imbalance. Record software
   revisions, effective parameters, logs and results before describing this variant as flight-tested.

## Known limitations and precautions

- This is a simulation model, not a validated hardware airframe or a hardware calibration source.
  Run actuator and flight procedures only in SITL with no real aircraft connected.
- Collision cylinders and the lumped base inertia are approximations. There is no modeled landing-leg
  suspension or separate leg mass. Physical fidelity has not been measured against an actual F550.
- Mesh rendering, reflected propeller visuals, sensor delivery, ground contact and closed-loop flight
  still require runtime verification. Static checks cannot replace those tests.
- Environment variables can override the default model, world or spawn pose. Check them if results
  differ from the files. Do not assume another variant's motor directions apply here.
- The original working PX4 model and its airframe should remain untouched. The XML repair belongs
  only to this variant; it does not repair the original installation's mesh.

## License and attribution

The copied MRS mesh assets are accompanied by [LICENSE_MRS](models/f550_patas/LICENSE_MRS),
the BSD 3-Clause license crediting the Multi-robot Systems (MRS) group at Czech Technical University
in Prague, copyright 2023. Retain the copyright, license conditions and disclaimer when redistributing.

The repository's [bundled mesh attribution](../../third_party/mrs_robots_description/README.md)
identifies `ctu-mrs/mrs_uav_gazebo_simulation` as the upstream source for its shared mesh collection.
This variant was copied from the local PX4 `f550` model; an exact upstream revision for all five local
meshes has not been independently established. Do not assume the shared collection's pinned commit
also documents the rotor housing and landing-leg meshes here. The XML escape is the only mesh edit
made while preparing this variant. This attribution does not establish a license for unrelated code.
