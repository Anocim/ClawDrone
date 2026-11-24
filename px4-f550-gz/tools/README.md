# Tools

## `gen_ca.py`

Generates the PX4 `CA_ROTORn_*` control-allocation parameters from the motor
plugins and link poses in one or more Gazebo SDF files. It prints the
`param set-default` lines to stdout; it does not modify any file.

Run it from `px4-f550-gz/`:

```bash
python3 tools/gen_ca.py \
  variants/f550/models/f550/model.sdf \
  variants/f550/models/f550_base/model.sdf --km 0.06

python3 tools/gen_ca.py \
  variants/f550_simple/models/f550_simple/model.sdf \
  variants/f550_simple/models/f550_base_simple/model.sdf --km 0.05
```

The `f550_patas` model is self-contained, so a single SDF is enough:

```bash
python3 tools/gen_ca.py variants/f550_patas/models/f550_patas/model.sdf --km 0.06
```

### Options

| Option | Meaning |
|---|---|
| `files` | One or more SDF files; motor plugins are read from all of them |
| `--km <value>` | Magnitude of the yaw moment constant `KM` (default `0.05`). Positive for CCW, negative for CW |
| `--observed <zones>` | Use observed motor mapping instead of the `actuator_number` declared in the SDF. Give the zone seen for output functions 101..106, comma separated: `front_right`, `right`, `back_right`, `back_left`, `left`, `front_left` |

Without `--observed` the declared `actuator_number` (or the deprecated
`motorNumber`) sets the motor index. The tool requires exactly six motors with
a `MulticopterMotorModel` plugin and warns if the spin directions do not
alternate around the vehicle.

### Conventions

- PX4 uses FRD axes, Gazebo uses FLU: `PY(PX4) = -y(Gazebo)`.
- `KM > 0` means CCW, `KM < 0` means CW, and must match
  `<turningDirection>` in the SDF.
- The PX4 motor index is the propeller/rotor number in the SDF.

To check the mapping in the simulator, run
`actuator_test set -f 101 -v 0.4 -t 3` (and 102 ... 106) in the PX4 shell with
the vehicle disarmed, then use `--observed` if the real mapping differs from
the declared one. Paste the generated lines into the corresponding airframe
file, rerun `./install.sh` and rebuild PX4. See each
[variant README](../variants/README.md) for its geometry and expected values.
