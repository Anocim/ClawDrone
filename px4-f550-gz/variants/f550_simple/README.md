# f550_simple

**Placeholder: this variant is intentionally empty for now.** `install.sh` skips it until it contains an airframe.

Planned content (see `../_template/README.md` for the full checklist):

```
variants/f550_simple/
|-- airframe/
|   `-- 4051_gz_f550_simple     # PX4 airframe, PX4_SIM_MODEL=f550_simple
`-- models/
    `-- f550_simple/
        |-- model.config
        `-- model.sdf
```

Once filled in, it is installed with `./install.sh --variant f550_simple` (or together with the others
using the default `--variant all`) and launched with:

```sh
make px4_sitl gz_f550_simple
```

Delete the two `.gitkeep` files after adding real content. Use an airframe ID that is not used by other
variants (`4050` belongs to `f550_detailed`) and model folder names different from the detailed variant's.
