#!/usr/bin/env bash
# =============================================================================
# setup_vision_env.sh - create the Python environment for f550_vision's detector
# =============================================================================
# USAGE
#   scripts/setup_vision_env.sh [--env PATH] [--cuda]
#
#   --env PATH  Where to create the virtual environment. Default: ~/yolo_env
#   --cuda      Install the default (CUDA) PyTorch build instead of the CPU-only
#               one. Only useful with an NVIDIA GPU; the download is several GB.
#
# The environment is created with --system-site-packages so rclpy stays visible.
# Build the workspace with it active (source PATH/bin/activate) so the node
# executables use this Python. Running the script again is safe.
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_DIR="$HOME/yolo_env"
CUDA=0

while [ $# -gt 0 ]; do
  case "$1" in
    --env)  ENV_DIR="${2:?missing path after --env}"; shift 2 ;;
    --cuda) CUDA=1; shift ;;
    -h|--help) sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 0 ;;
    *) echo "Unknown argument: $1 (try --help)"; exit 1 ;;
  esac
done

command -v python3 >/dev/null || { echo "ERROR: python3 not found"; exit 1; }
python3 -c "import venv" 2>/dev/null || { echo "ERROR: install it with: sudo apt install python3-venv"; exit 1; }

echo "--> Creating $ENV_DIR"
python3 -m venv --system-site-packages "$ENV_DIR"
PIP="$ENV_DIR/bin/python -m pip"     # no 'source activate': it breaks with set -u

$PIP install --upgrade pip
$PIP install "numpy<2"
if [ "$CUDA" = 0 ]; then
  echo "--> Installing CPU-only PyTorch"
  $PIP install torch torchvision --index-url https://download.pytorch.org/whl/cpu
fi
$PIP install -r "$HERE/requirements-vision.txt"

echo
echo "Done. Activate it before building or running the detector:"
echo "  source $ENV_DIR/bin/activate"
