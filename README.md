# px4-f550-gz

DJI F550 hexacopter simulation models for **PX4 SITL + Gazebo Sim**, including two model variants, PX4 airframes and an installer to integrate them into a PX4-Autopilot installation.

> **Tested with:**
> - Ubuntu 22.04.5 LTS
> - PX4-Autopilot `v1.18.0-beta1-1084-g95ede794c0`
> - Gazebo Sim 8.10.0
> - ROS 2 Humble (installed in the development environment)

Both F550 variants have been successfully launched in Gazebo with PX4 SITL.

## Repository layout

```text
px4-f550-gz/
|-- install.sh                    # Installs the models and airframes into PX4
|-- tools/
|   `-- gen_ca.py                 # Generates control allocation parameters
|-- variants/
|   |-- f550_detailed/            # Detailed F550 simulation model
|   |   |-- airframe/             # PX4 airframe configuration
|   |   |-- models/               # Gazebo model files
|   |   `-- README.md             # Model-specific information
|   |-- f550_simple/              # Simplified F550 simulation model
|   |   |-- airframe/
|   |   `-- models/
|   `-- _template/                # Template for creating new variants
`-- third_party/
    `-- mrs_robots_description/   # External 3D meshes and license
```

## Simulation variants

Two F550 configurations are currently available:

| Variant | Description | Status |
|---|---|---|
| `f550_detailed` | Detailed model with sensors, motor plugins and 3D meshes | Tested |
| `f550_simple` | Simplified F550 model | Tested |

Both variants have been successfully launched using Gazebo Sim and PX4 SITL.

The installer provides a list of the available variants:

```sh
./install.sh --list
```

**Note:** Both airframe configurations currently use the `gz_f550` Make target. Install and test the variants individually to avoid conflicts between their PX4 and Gazebo model files.

## Installation

### 1. PX4-Autopilot setup

Clone PX4-Autopilot and check out the version used for development:

```sh
git clone --recursive https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot
cd ~/PX4-Autopilot

git checkout 95ede794c0
git submodule update --init --recursive
```

Install the PX4 dependencies:

```sh
bash Tools/setup/ubuntu.sh
```

Before installing the F550 models, verify that the standard Gazebo simulation works:

```sh
make px4_sitl gz_x500
```

If the standard PX4 simulation does not launch, check the PX4 and Gazebo installation first.

### 2. Clone this repository

```sh
git clone -b Simulation_Control https://github.com/Anocim/ClawDrone.git
cd ClawDrone/px4-f550-gz
```

### 3. Install an F550 variant

List the available variants:

```sh
./install.sh --list
```

Install the detailed model:

```sh
./install.sh --px4 ~/PX4-Autopilot --variant f550_detailed
```

Or install the simplified model:

```sh
./install.sh --px4 ~/PX4-Autopilot --variant f550_simple
```

The installer handles the integration of the selected model into the PX4 installation, including its Gazebo model files and PX4 airframe configuration.

Available installer options:

| Option | Description |
|---|---|
| `--px4 <path>` | Specifies the PX4-Autopilot directory |
| `--variant <name>` | Installs a specific variant |
| `--list` | Lists available variants |
| `--no-meshes` | Skips the bundled 3D meshes |
| `--uninstall` | Reverts the installation |
| `--help` | Displays installer help |

The default PX4 directory is `~/PX4-Autopilot`.

## Running the simulation

After installing one of the variants, launch the F550 simulation from the PX4-Autopilot directory:

```sh
cd ~/PX4-Autopilot
make px4_sitl gz_f550
```

PX4 SITL starts alongside Gazebo Sim, loading the selected F550 model and its corresponding airframe configuration.

The PX4 shell (`pxh>`) can be used to inspect the vehicle and its simulation status.

## Verification

The following points have been verified during development:

- Both F550 variants launch successfully in Gazebo Sim.
- PX4 SITL starts with the F550 simulation.
- The models are loaded through the PX4 Gazebo simulation interface.
- The simulation environment runs with the tested PX4 and Gazebo versions.

For PX4 parameter inspection, use the PX4 shell:

```sh
param show CA_ROTOR0_PY
param show CA_ROTOR4_KM
```

The expected values depend on the selected airframe configuration.

## 3D meshes

The detailed model uses external 3D mesh resources bundled under:

```text
third_party/mrs_robots_description/
```

These resources provide the visual geometry used by the simulation model. They are separate from the PX4 airframe configuration.

Keep the mesh directory and its license file together when distributing the repository.

## Troubleshooting

| Symptom | Possible cause | Suggested action |
|---|---|---|
| `gz_f550` target not found | Airframe not registered in PX4 | Run the installer again and rebuild |
| Gazebo does not load the F550 model | Model files are missing or incorrectly installed | Check the selected variant and rerun the installer |
| PX4 loads unexpected parameters | Parameters from a previous simulation are still stored | Check the installed airframe and saved PX4 parameters |
| 3D meshes are missing | Mesh resources were not installed | Reinstall without `--no-meshes` |
| Standard `gz_x500` simulation fails | PX4 or Gazebo setup problem | Verify the PX4 installation before debugging this repository |

## Adding a new variant

New simulation configurations can be added under `variants/`.

The `_template/` directory provides a starting point for creating a new model variant. Each variant should contain its own:

- Gazebo model files.
- PX4 airframe configuration.
- Model-specific documentation, when necessary.

Use unique model names and airframe IDs to avoid conflicts with existing configurations.

## Development status

The current development environment supports:

- PX4 SITL.
- Gazebo Sim 8.
- DJI F550 detailed and simplified models.
- ROS 2 Humble installation.

Both F550 models are already running in the simulation environment. Further work will focus on developing and testing the vehicle control system within this simulation setup.

## References

- [PX4-Autopilot](https://github.com/PX4/PX4-Autopilot)
- [PX4 Gazebo Simulation](https://docs.px4.io/main/en/sim_gazebo_gz/)
- [Gazebo Sim](https://gazebosim.org/docs)
- [ROS 2 Humble](https://docs.ros.org/en/humble/)

## License and credits

The bundled MRS mesh resources are distributed under their respective license, included in `third_party/mrs_robots_description/`.

Refer to the corresponding license files before redistributing third-party resources.