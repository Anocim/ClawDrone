# Variant template

Copy this folder to `variants/<your_variant>/`. See the
[variants index](../README.md) for the list of existing variants and their
IDs. Create:

```
variants/<your_variant>/
|-- airframe/
|   `-- 40NN_gz_<model>          # PX4 airframe; PX4_SIM_MODEL must equal <model>
`-- models/
    `-- <model>/
        |-- model.config
        `-- model.sdf            # Gazebo model (plus any extra model folders it includes)
```

Checklist:

1. Pick a free numeric ID `40NN` (it is checked at install time) and a model name that does not clash with other variants.
2. In the airframe: `PX4_SIM_MODEL=${PX4_SIM_MODEL:=<model>}`, `CA_ROTOR_COUNT`, the `CA_ROTORn_*` geometry
   (generate it with `tools/gen_ca.py`) and the `SIM_GZ_EC_*` output mapping.
3. Folders in `models/` are copied as-is to `PX4-Autopilot/Tools/simulation/gz/models/`.
4. Add a `README.md` in the variant with its motor layout and make target.
5. If your SDF uses `model://mrs_robots_description/...`, the installer copies the bundled meshes automatically;
   add any extra mesh you need to `third_party/mrs_robots_description/` keeping the upstream sub-paths.
6. If the new model extends another variant, add a `requires` file containing that base variant's
   folder name (one per line). The installer then installs the base automatically. The
   `*_mono_cam_down` variants are examples.
7. Check with `./install.sh --list`, then `./install.sh --variant <your_variant>` (folder name).
