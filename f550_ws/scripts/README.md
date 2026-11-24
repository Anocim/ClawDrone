# Helper scripts

## `setup_vision_env.sh`

Creates the Python virtual environment used by the YOLO detector in
[`f550_vision`](../src/f550_vision/README.md).

```bash
# From f550_ws/
scripts/setup_vision_env.sh                 # creates ~/yolo_env, CPU-only PyTorch
scripts/setup_vision_env.sh --cuda          # NVIDIA GPU build
scripts/setup_vision_env.sh --env /path/to/env
scripts/setup_vision_env.sh --help
```

The environment is created with `--system-site-packages` so that `rclpy` stays
visible. The script installs `numpy<2`, PyTorch (from the CPU index unless
`--cuda` is given) and the packages listed in
[`../requirements-vision.txt`](../requirements-vision.txt). It is safe to run
again.

Activate the environment **before building and running** the workspace so the
`f550_vision` executables use that Python:

```bash
source ~/yolo_env/bin/activate
cd f550_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

See [`INSTALL.md`](../INSTALL.md) for the full dependency installation and
[`README.md`](../README.md) for the complete launch example.
