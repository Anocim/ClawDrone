#!/usr/bin/env bash
# =============================================================================
# install.sh - install the drone variants of this repository into PX4-Autopilot
# =============================================================================
#
# WHY THIS SCRIPT EXISTS
#   For `make px4_sitl gz_<name>` to work, PX4 needs four things that live
#   inside the PX4-Autopilot checkout, not in this repository:
#
#     1. A Gazebo model            -> Tools/simulation/gz/models/<model>/
#        (the SDF: bodies, inertia, propellers, sensors, motor plugins)
#     2. A PX4 airframe file       -> ROMFS/px4fmu_common/init.d-posix/airframes/<ID>_gz_<name>
#        (rotor geometry CA_ROTORn_*, motor outputs, hover throttle, spawn pose)
#     3. The airframe name listed in ROMFS/.../airframes/CMakeLists.txt
#        (otherwise it is not packaged into the build and the make target
#        `gz_<name>` does not exist)
#     4. Optional meshes           -> Tools/simulation/gz/models/mrs_robots_description/
#        (only for the 3D visuals; the physics does not depend on them)
#
#   This script copies those files from this repository into the right places
#   and registers the airframe, so nobody has to do it by hand.
#
# WHAT IS A "VARIANT"
#   A variant is a folder variants/<name>/ containing:
#       airframe/   one or more PX4 airframe files (e.g. 4050_gz_f550)
#       models/     one or more Gazebo model folders (e.g. f550/, f550_base/)
#   Any folder in variants/ that has at least one airframe file is picked up
#   automatically; this script never needs editing to add a variant.
#   Folders starting with "_" (e.g. _template) and variants without an airframe
#   file (e.g. the empty f550_simple placeholder) are ignored.
#
# USAGE
#   ./install.sh [--px4 PATH] [--variant NAME|all] [--no-meshes] [--uninstall]
#   ./install.sh --list
#
# OPTIONS
#   --px4 PATH     Path to your PX4-Autopilot checkout. Default: ~/PX4-Autopilot
#   --variant NAME Install only this variant. Default: all (every installable variant).
#   --no-meshes    Do not copy the bundled meshes (third_party/mrs_robots_description).
#   --uninstall    Remove what a previous install copied and the CMakeLists.txt line.
#                  The bundled meshes are removed only with --variant all (they may
#                  be shared by several variants).
#   --list         Show the variants and the `make` target of each, then exit.
#   -h, --help     Show this header.
#
# EXAMPLES
#   ./install.sh --list
#   ./install.sh                                  # everything, PX4 in ~/PX4-Autopilot
#   ./install.sh --px4 /opt/PX4-Autopilot --variant f550_detailed
#   ./install.sh --uninstall
#
# GOOD TO KNOW
#   * It only touches files inside the PX4 checkout you point it to.
#   * It is idempotent: running it twice gives the same result (files are
#     overwritten, the CMakeLists.txt line is added only once).
#   * Tools/simulation/gz is a git submodule in recent PX4 versions. Copying
#     models into it makes `git status` show it as modified; this is harmless.
#     Running `git submodule update` there may remove untracked files, so just
#     run this script again afterwards.
#   * It also cleans leftovers that break the launch (see "STALE FILES" below).
#   * After installing, run the make target printed at the end.
#
# STALE FILES (why `make px4_sitl gz_f550` can fail while `gz_f550_simple` works)
#   PX4 finds the airframe for a make target by listing
#   build/px4_sitl_default/etc/init.d-posix/airframes and matching "<ID>_<target>".
#   An old file such as 4051_gz_f550 (the previous name of the simple variant)
#   makes the target gz_f550 match TWO airframes (4050 and 4051), so the detailed
#   model cannot start, while gz_f550_simple is not affected. PX4 copies airframes
#   into the build folder but never deletes them, so such leftovers survive.
#   This script removes (a) the legacy airframe names listed in LEGACY_AIRFRAMES
#   and (b) any *_gz_* airframe in the build folder that no longer exists in ROMFS.
# =============================================================================
set -euo pipefail   # stop at the first error, on unset variables, and on failed pipes

# ----------------------------------------------------------------------------
# 0. Defaults and command-line parsing
# ----------------------------------------------------------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # folder of this repository
PX4_DIR="$HOME/PX4-Autopilot"
VARIANT="all"
WITH_MESHES=1
UNINSTALL=0
LIST=0

while [ $# -gt 0 ]; do
  case "$1" in
    --px4)       PX4_DIR="${2:?missing path after --px4}"; shift 2 ;;
    --variant)   VARIANT="${2:?missing name after --variant}"; shift 2 ;;
    --no-meshes) WITH_MESHES=0; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --list)      LIST=1; shift ;;
    -h|--help)   sed -n '2,/^set -euo/p' "$0" | sed '$d'; exit 0 ;;
    *) echo "Unknown argument: $1 (try --help)"; exit 1 ;;
  esac
done

# ----------------------------------------------------------------------------
# Helpers that inspect the variants/ folder
# ----------------------------------------------------------------------------

# Airframe files of a variant (ignores hidden files such as .gitkeep).
variant_airframes() {
  find "$HERE/variants/$1/airframe" -maxdepth 1 -type f ! -name '.*' -printf '%f\n' 2>/dev/null | sort || true
}

# Model folders of a variant (ignores hidden entries).
variant_models() {
  find "$HERE/variants/$1/models" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -printf '%f\n' 2>/dev/null | sort || true
}

# All variant folders except the ones starting with "_" (templates).
all_variant_dirs() {
  for d in "$HERE"/variants/*/; do
    n="$(basename "$d")"
    case "$n" in _*) continue ;; esac
    echo "$n"
  done
}

# Variants that contain at least one airframe file, i.e. that can be installed.
installable_variants() {
  for n in $(all_variant_dirs); do
    # NOTE: written as "if" on purpose. "[ ... ] && echo" would return 1 for the
    # last empty variant and, with "set -e", silently abort the whole script.
    if [ -n "$(variant_airframes "$n")" ]; then echo "$n"; fi
  done
}

# Does this variant's SDF refer to the bundled MRS meshes?
variant_needs_meshes() {
  grep -rqs "model://mrs_robots_description" "$HERE/variants/$1/models"
}

# ----------------------------------------------------------------------------
# --list : show what this repository provides, then exit
# ----------------------------------------------------------------------------
if [ "$LIST" = 1 ]; then
  for n in $(all_variant_dirs); do
    if [ -z "$(variant_airframes "$n")" ]; then
      echo "$n   ->   (empty placeholder, nothing to install yet)"
      continue
    fi
    for af in $(variant_airframes "$n"); do
      # Airframe file "4050_gz_f550" -> make target "gz_f550"
      echo "$n   ->   make px4_sitl ${af#*_}"
    done
  done
  exit 0
fi

# ----------------------------------------------------------------------------
# 1. Decide which variants to process
# ----------------------------------------------------------------------------
if [ "$VARIANT" = "all" ]; then
  SELECTED="$(installable_variants)"
  for n in $(all_variant_dirs); do
    # (here-strings instead of pipes: "grep -q" exits early and, with pipefail, a pipe would report failure)
    grep -qx "$n" <<< "$SELECTED" || echo "--> Skipping '$n': it has no airframe file yet (placeholder)"
  done
else
  ALL_VARIANTS="$(all_variant_dirs)"
  grep -qx "$VARIANT" <<< "$ALL_VARIANTS" || { echo "ERROR: unknown variant '$VARIANT'. Available:"; sed 's/^/  /' <<< "$ALL_VARIANTS"; exit 1; }
  [ -n "$(variant_airframes "$VARIANT")" ] || { echo "ERROR: variant '$VARIANT' is an empty placeholder (no file in variants/$VARIANT/airframe/)."; exit 1; }
  SELECTED="$VARIANT"
fi
[ -n "$SELECTED" ] || { echo "ERROR: no installable variants found in $HERE/variants"; exit 1; }

# ----------------------------------------------------------------------------
# 2. Check that PX4_DIR really is a PX4-Autopilot checkout
# ----------------------------------------------------------------------------
AIRFRAMES="$PX4_DIR/ROMFS/px4fmu_common/init.d-posix/airframes"
MODELS="$PX4_DIR/Tools/simulation/gz/models"
CMAKE="$AIRFRAMES/CMakeLists.txt"
BUILD_AF="$PX4_DIR/build/px4_sitl_default/etc/init.d-posix/airframes"   # copy PX4 reads at runtime

# Airframe names used by earlier versions of this repository. They collide with the
# current ones (same make target or same ID), so they are removed on install/uninstall.
LEGACY_AIRFRAMES="4051_gz_f550"

[ -d "$AIRFRAMES" ] || { echo "ERROR: $PX4_DIR does not look like PX4-Autopilot (missing $AIRFRAMES). Use --px4 PATH."; exit 1; }
[ -d "$MODELS" ]    || { echo "ERROR: missing $MODELS. Run 'git submodule update --init --recursive' inside PX4-Autopilot."; exit 1; }
[ -f "$CMAKE" ]     || { echo "ERROR: missing $CMAKE"; exit 1; }

# ----------------------------------------------------------------------------
# Helpers that edit airframes/CMakeLists.txt (the list of packaged airframes)
# ----------------------------------------------------------------------------

# Add "<id>" to the airframe list, right after 4001_gz_x500 (the stock Gazebo
# quadcopter), unless it is already there.
register_airframe() {
  local id="$1"
  if grep -qE "^[[:space:]]*$id[[:space:]]*$" "$CMAKE"; then
    echo "    $id already registered in CMakeLists.txt"
  elif grep -qE "^[[:space:]]*4001_gz_x500[[:space:]]*$" "$CMAKE"; then
    # awk prints every line and, after the 4001_gz_x500 line, one extra line with our ID.
    awk -v id="$id" '{print} /^[ \t]*4001_gz_x500[ \t]*$/ {print "\t" id}' "$CMAKE" > "$CMAKE.tmp"
    mv "$CMAKE.tmp" "$CMAKE"
    echo "    $id added to CMakeLists.txt (after 4001_gz_x500)"
  else
    # PX4 layout changed: do not guess, tell the user what to do.
    echo "    WARNING: 4001_gz_x500 not found in $CMAKE."
    echo "    Add the line '$id' manually next to the other *_gz_* airframes."
  fi
}

# Remove "<id>" from the list (used by --uninstall).
unregister_airframe() {
  sed -i "/^[[:space:]]*$1[[:space:]]*$/d" "$CMAKE"
}

# Remove airframes this repository used in the past (ROMFS file, CMakeLists.txt line, build copy).
clean_legacy_airframes() {
  for id in $LEGACY_AIRFRAMES; do
    if [ -e "$AIRFRAMES/$id" ] || [ -e "$BUILD_AF/$id" ] || grep -qE "^[[:space:]]*$id[[:space:]]*$" "$CMAKE"; then
      echo "--> Removing legacy airframe $id (old name used by this repo; it would clash with the current ones)"
      rm -f "$AIRFRAMES/$id" "$BUILD_AF/$id"
      unregister_airframe "$id"
    fi
  done
}

# PX4 copies airframes into the build folder but never deletes them. Remove the *_gz_* copies
# that no longer have a source file in ROMFS, otherwise a ghost airframe can make a target ambiguous.
clean_stale_build_airframes() {
  [ -d "$BUILD_AF" ] || return 0
  for f in "$BUILD_AF"/*_gz_*; do
    [ -e "$f" ] || continue
    b="$(basename "$f")"
    if [ ! -e "$AIRFRAMES/$b" ]; then
      echo "--> Removing stale build copy of airframe $b (no longer in ROMFS)"
      rm -f "$f"
    fi
  done
}

# ----------------------------------------------------------------------------
# 3. Install (or uninstall) every selected variant
# ----------------------------------------------------------------------------
clean_legacy_airframes
NEED_MESHES=0
for v in $SELECTED; do
  VDIR="$HERE/variants/$v"

  # ---- uninstall branch ----
  if [ "$UNINSTALL" = 1 ]; then
    echo "--> Uninstalling variant '$v'"
    for id in $(variant_airframes "$v"); do
      rm -f "$AIRFRAMES/$id"
      unregister_airframe "$id"
      echo "    removed airframe $id"
    done
    for m in $(variant_models "$v"); do
      rm -rf "$MODELS/$m"
      echo "    removed model $m"
    done
    continue
  fi

  # ---- install branch ----
  echo "--> Installing variant '$v'"

  # 3a. Safety check. PX4 identifies an airframe by its numeric prefix (4050,
  #     4051, ...). If a different airframe already uses our number, the two
  #     would clash, so stop and ask for a rename instead of overwriting.
  for id in $(variant_airframes "$v"); do
    prefix="${id%%_*}"
    for other in "$AIRFRAMES/${prefix}_"*; do
      [ -e "$other" ] || continue
      if [ "$(basename "$other")" != "$id" ]; then
        echo "ERROR: airframe ID $prefix is already used by $(basename "$other")."
        echo "       Rename the file in variants/$v/airframe/ (and its PX4_SIM_MODEL / make target) to a free number."
        exit 1
      fi
    done
  done

  #     The make target is the part after the ID ("4050_gz_f550" -> "gz_f550"). Two airframes with
  #     the same target but different IDs make that target ambiguous for PX4, so refuse too.
  for id in $(variant_airframes "$v"); do
    target="${id#*_}"
    for other in "$AIRFRAMES"/[0-9]*_"$target"; do
      [ -e "$other" ] || continue
      if [ "$(basename "$other")" != "$id" ]; then
        echo "ERROR: make target '$target' would be ambiguous: $(basename "$other") already provides it."
        echo "       Remove that airframe from PX4 or rename the one in variants/$v/airframe/."
        exit 1
      fi
    done
  done

  # 3b. Gazebo models. Each folder in variants/<v>/models/ is copied as-is to
  #     PX4's models directory. "cp -r dir/." also copies hidden files.
  for m in $(variant_models "$v"); do
    mkdir -p "$MODELS/$m"
    cp -r "$VDIR/models/$m/." "$MODELS/$m/"
    echo "    model $m -> $MODELS/$m"
  done

  # 3c. Airframe file(s) + registration in CMakeLists.txt.
  for id in $(variant_airframes "$v"); do
    cp "$VDIR/airframe/$id" "$AIRFRAMES/$id"
    echo "    airframe $id -> $AIRFRAMES/$id"
    register_airframe "$id"
  done

  if variant_needs_meshes "$v"; then NEED_MESHES=1; fi
done

clean_stale_build_airframes

# ----------------------------------------------------------------------------
# 4. Meshes (visual only)
#    The SDF files point to model://mrs_robots_description/meshes/...  Gazebo
#    resolves "model://<name>" by looking for a folder <name> inside its model
#    search path, and PX4 already adds Tools/simulation/gz/models to that path.
#    So copying the bundled folder there is all that is needed.
#    Without them the drone still simulates, but "mesh not found" warnings
#    appear and the visuals are missing.
# ----------------------------------------------------------------------------
MESH_SRC="$HERE/third_party/mrs_robots_description"
MESH_DST="$MODELS/mrs_robots_description"

if [ "$UNINSTALL" = 1 ]; then
  if [ "$VARIANT" = "all" ]; then
    rm -rf "$MESH_DST"
    echo "--> Removed bundled meshes"
  else
    echo "--> Bundled meshes kept (other variants may use them; use --variant all to remove them too)"
  fi
elif [ "$NEED_MESHES" = 1 ] && [ "$WITH_MESHES" = 1 ]; then
  [ -d "$MESH_SRC/meshes" ] || { echo "ERROR: bundled meshes missing in $MESH_SRC. Re-clone the repository."; exit 1; }
  echo "--> Installing bundled meshes (BSD-3-Clause, CTU MRS) -> $MESH_DST"
  mkdir -p "$MESH_DST"
  cp -r "$MESH_SRC/." "$MESH_DST/"
elif [ "$NEED_MESHES" = 1 ]; then
  echo "--> --no-meshes given: the simulation works the same, only the 3D visuals will be missing."
fi

# ----------------------------------------------------------------------------
# 5. Remove parameters PX4 saved in previous runs
#    `param set-default` in the airframe only sets DEFAULT values. A value that
#    was saved explicitly (e.g. `param set CA_ROTOR0_PY ...` followed by
#    `param save`) is stored in build/px4_sitl_default/rootfs/parameters*.bson
#    and wins over the default. Deleting these files (and the dataman database)
#    guarantees a clean start. Note: when SYS_AUTOSTART changes (switching
#    variants) PX4 already resets its parameters by itself.
# ----------------------------------------------------------------------------
echo "--> Removing parameters saved by previous PX4 runs (if any)"
rm -f "$PX4_DIR"/build/px4_sitl_default/rootfs/parameters*.bson \
      "$PX4_DIR"/build/px4_sitl_default/rootfs/dataman

# ----------------------------------------------------------------------------
# 6. Tell the user what to run next
# ----------------------------------------------------------------------------
echo
if [ "$UNINSTALL" = 1 ]; then
  echo "Done. Rebuild PX4 (make px4_sitl gz_x500) so the build forgets the removed airframes."
else
  echo "Done. The first build recompiles because CMakeLists.txt changed. Launch with:"
  for v in $SELECTED; do
    for id in $(variant_airframes "$v"); do
      echo "  cd $PX4_DIR && make px4_sitl ${id#*_}"
    done
  done
  echo "If make says the target does not exist: rm -f $PX4_DIR/build/px4_sitl_default/CMakeCache.txt and retry."
fi
