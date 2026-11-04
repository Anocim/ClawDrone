#!/usr/bin/env python3
"""
Generate the PX4 CA_ROTORn parameters from the model SDF file(s).

Usage:
  python3 gen_ca.py MODEL.sdf [MODEL_BASE.sdf ...] [--km 0.06]
  python3 gen_ca.py MODEL.sdf MODEL_BASE.sdf --observed left,right,back_right,front_left,back_left,front_right

Without --observed the motor index declared in the SDF (actuator_number or
motorNumber, the deprecated name) is used.

--observed lists, for output functions 101..106 in that order, which propeller
you see spinning when running in the PX4 shell:
    actuator_test set -f 10X -v 0.4 -t 3
Positions are seen from the drone looking along +X (right = Gazebo -Y).
Valid values: front_right, right, back_right, back_left, left, front_left

PX4 uses FRD axes and Gazebo uses FLU, hence PY(PX4) = -y(Gazebo).
KM > 0 means CCW, KM < 0 means CW.
"""
import sys, math, argparse
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser()
p.add_argument("files", nargs="+")
p.add_argument("--observed", default=None)
p.add_argument("--km", type=float, default=0.05)
a = p.parse_args()

links, plugins = {}, {}
for f in a.files:
    root = ET.parse(f).getroot()
    for l in root.iter("link"):
        pose = l.find("pose")
        if pose is not None and pose.text:
            v = [float(t) for t in pose.text.split()]
            links[l.get("name")] = (v[0], v[1])
    for pl in root.iter("plugin"):
        if "MulticopterMotorModel" not in (pl.get("name") or ""):
            continue
        ln = pl.findtext("linkName")
        idx = pl.findtext("actuator_number")
        tag = "actuator_number"
        if idx is None:
            idx, tag = pl.findtext("motorNumber"), "motorNumber"
        plugins[ln] = dict(dir=(pl.findtext("turningDirection") or "").strip(), idx=idx, tag=tag)

props = {n: xy for n, xy in links.items() if n in plugins}
if len(props) != 6:
    sys.exit(f"Found {len(props)} propellers with a motor plugin (expected 6): {list(props)}")

def zone(x, y):
    if abs(x) < 0.05:
        return "left" if y > 0 else "right"
    return ("front_" if x > 0 else "back_") + ("left" if y > 0 else "right")

by_zone = {zone(*xy): n for n, xy in props.items()}

print("# Propellers found in the SDF:")
for n, xy in sorted(props.items()):
    pl = plugins[n]
    print(f"#  {n:12s} pos=({xy[0]:+.4f},{xy[1]:+.4f}) {zone(*xy):12s} spin={pl['dir']:3s} {pl['tag']}={pl['idx']}")
print()

if a.observed:
    order = [z.strip() for z in a.observed.split(",")]
    if sorted(order) != sorted(by_zone):
        sys.exit(f"--observed must contain exactly: {sorted(by_zone)}")
    seq = [by_zone[z] for z in order]
    print("# Mode: OBSERVED mapping (functions 101..106)")
else:
    seq = sorted(props, key=lambda n: int(plugins[n]["idx"]))
    print("# Mode: mapping DECLARED in the SDF")

for i, n in enumerate(seq):
    x, y = props[n]
    km = a.km if plugins[n]["dir"] == "ccw" else -a.km
    print(f"param set-default CA_ROTOR{i}_PX {x:.4f}")
    print(f"param set-default CA_ROTOR{i}_PY {-y:.4f}")   # FLU -> FRD
    print(f"param set-default CA_ROTOR{i}_KM {km}")
print()
ring = sorted(props, key=lambda n: math.atan2(props[n][1], props[n][0]))
dirs = [plugins[n]["dir"] for n in ring]
if any(dirs[i] == dirs[(i + 1) % 6] for i in range(6)):
    print("# WARNING: spin directions do NOT alternate around the drone:", list(zip(ring, dirs)))
