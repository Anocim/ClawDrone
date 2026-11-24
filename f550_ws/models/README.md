# Model weights

Put your Ultralytics `.pt` file here, for example `best.pt`. The folder exists
in the repository so everyone knows where weights belong, but its contents are
**not tracked by Git**: this directory's `.gitignore` ignores everything except
`.gitkeep`, `.gitignore` and this README. Each checkout supplies its own file.

Run the detector with the absolute path to that file:

```bash
cd ~/ClawDrone/f550_ws
source /opt/ros/humble/setup.bash
source ~/yolo_env/bin/activate
source install/setup.bash
ros2 launch f550_vision detector.launch.py model_path:=$PWD/models/best.pt
```

You can check the file before launching with:

```bash
python3 -c "from ultralytics import YOLO; print(YOLO('models/best.pt').names)"
```

If several models are needed, keep them here with distinct names and select
the one to use with `model_path:=`. Check the license of the weights and of
the dataset they were trained on before sharing them. For a canonical model
shared across machines, use Git LFS or a release asset instead of this folder.

See [`INSTALL.md`](../INSTALL.md) for the Python environment and
[`f550_vision/README.md`](../src/f550_vision/README.md) for detector options.
