# ClawDrone

Development and programming of an autonomous drone capable of detecting tennis balls from the air, navigating toward them, picking them up, and transporting and dropping them into a designated basket.

> **Phase 1 — Requirement Analysis** (first step of the V-diagram). This document is the formal description and organisation of the project: the mission, the high-level requirements, and how the work is split into departments and interconnected. Design, implementation, integration, and verification are later phases. See the V-diagram in [`Pictures/v-diagram.png`](Pictures/v-diagram.png).

## 1. Mission & Concept of Operations

The system is an autonomous multirotor equipped with a claw that finds tennis balls on the ground, grasps them, and drops them into a designated basket. The drone carries **one ball per trip**, so the mission is a short cyclic task repeated until the battery requires landing.

High-level mission sequence:

1. **Take off** and reach a safe search altitude.
2. **Search** the area for tennis balls.
3. **Detect** a tennis ball and estimate its 3D position.
4. **Approach** the ball and **align** precisely above it.
5. **Grasp** the ball with the claw.
6. **Transport** the ball to the designated basket (known destination).
7. **Release** the ball into the basket.
8. **Repeat** from step 2 until the battery requires a landing; then **land** safely.

## 2. Objectives

- **Primary objective:** complete the autonomous cycle of detecting, grasping, transporting, and dropping tennis balls.
- **Secondary objective (stretch):** implement route optimization to collect the balls along the shortest possible path, completing the task faster. This is an optional enhancement, not part of the core requirements.
- **Success criteria (high level):** the mission sequence above can be performed autonomously, with the drone safely returning/landing. Quantitative targets are **TBD** (see [Open questions](#7-open-questions--tbd)).

## 3. High-level requirements

### Functional

- Detect tennis balls from the air.
- Estimate the 3D position of a detected ball.
- Navigate toward the ball and align precisely above it.
- Actuate the claw to grasp the ball.
- Hold the ball while flying.
- Transport the ball to the designated basket.
- Release the ball into the basket.

### Performance (all targets TBD)

- Payload and claw grasp capability: **TBD**
- Flight time per mission: **TBD**
- Ball detection rate and range: **TBD**
- Grasp success rate: **TBD**
- Mission cycle time (per ball): **TBD**
- Positioning/alignment accuracy: **TBD**

### Constraints & assumptions

- **PX4** is the autopilot.
- **Gazebo** is the official integration testbed (see [§5](#5-department-interconnections)).
- Perception is **camera-based** (Vision department).
- Target operation environment, lighting conditions, and applicable drone regulations: **TBD**.
- Assumed ball properties (size, colour) as per a standard tennis ball.

## 4. System organisation into departments

| Department | Responsibility | Main input / output |
|---|---|---|
| **PX4 (autopilot)** | FC firmware and parameters, state estimation (EKF2), flight modes, offboard/position control, failsafes, MAVLink comms, and the ROS 2 integration/comms-software stack. | In: sensor data, target setpoints. Out: actuator commands, telemetry/state. |
| **Sensors** | Platform state/navigation sensors (IMU, barometer, magnetometer, GNSS, optical flow, rangefinder/ToF): selection, mounting, calibration, PX4 driver config. | In: environment, power. Out: sensor streams to PX4 EKF2. |
| **Vision** | Camera-based detection and 3D localization of tennis balls, alignment error, grasp-trigger logic, and coordinate transforms. | In: camera frames, vehicle state. Out: ball pose + confidence, grasp trigger. |
| **Claw — mechanical engineering** | Gripper design, actuation mechanism, materials, mounting to the airframe, CoG/payload, ball retention and release. | In: servo/power specs, ball properties. Out: CAD/model, mechanical interface, mass/CoG spec. |
| **Electronics** | Power architecture (battery → PDB → BEC), ESCs, servo driver, companion-computer hardware, wiring harness, connectors, current/grasp sensing. | In: power/actuator/signal requirements. Out: power rails, wired harness, servo signal path. |
| **Simulation (Gazebo)** | World, drone + claw + camera models, sensor plugins, and bridges (PX4 SITL and ROS 2). | In: models and specs from other departments. Out: simulated sensors, camera feed, physics. |

**Future department — Mission manager.** The mission/state machine (takeoff → search → align → grasp → drop) is not owned by any current department and will be a dedicated department later. Its interfaces are reserved now so they can be connected without rework.

> Ownership notes: **Sensors** covers platform *state* estimation; **Vision** owns the *camera + perception* pipeline. **Electronics** owns the companion-computer *hardware*; **PX4** owns the *ROS 2 software/integration* stack.

## 5. Department interconnections

The departments interconnect across three layers:

- **Physical / power** — Electronics is the hub: battery, power rails, harness, and connectors feed PX4, the claw servo, the companion computer, and the sensors.
- **Data / comms** — two buses matter:
  - **MAVLink / uXRCE-DDS (or MAVROS)** between **PX4 ↔ companion computer** (state, arming, offboard setpoints).
  - **ROS 2 topics/services** on the companion (Vision → target, Vision → grasp command, grasp feedback → mission logic).
- **Simulation** — Gazebo is a cross-cutting testbed, not a silo. Everything is validated in simulation first (*simulation-first*).

### Interface register

| ID | From → To | What | How |
|---|---|---|---|
| I1 | Sensors → PX4 | IMU/baro/mag/GNSS/flow/range data | I2C/SPI/UART/CAN → PX4 drivers → EKF2 |
| I2 | Camera → Vision | Video frames (real or sim) | CSI/USB (sim: ROS 2 image topic) |
| I3 | Vision → PX4 | Ball pose + confidence, alignment error | ROS 2 topic → offboard setpoint (uXRCE-DDS/MAVROS) |
| I4 | PX4 → Vision | Vehicle state, arming/failsafe | MAVLink / ROS 2 |
| I5 | PX4 → Electronics | Motor + claw servo commands | PWM/DShot/CAN |
| I6 | Electronics → Claw | Servo power + signal | Harness/connector |
| I7 | Claw → Vision | Grasp confirmation | Limit switch / current sense → ROS 2 |
| I8 | Electronics → all | Regulated power rails | Battery → PDB → BEC |
| I9 | Mechanical → Electronics | Actuator/connector spec | Interface drawing |
| I10 | Mechanical → Gazebo | CAD, mass/Claw joint model | SDF/URDF |
| I11 | Gazebo → PX4 | Simulated sensors/actuators | PX4 SITL + gz bridge |
| I12 | Gazebo → Vision | Simulated camera | ROS 2 bridge |
| I13 | Vision → Electronics/Claw | Grasp trigger | ROS 2 → servo driver |

### Standards to fix early

- **Coordinate frames**: PX4 uses NED/FRD while ROS 2 uses ENU/FLU. Agree on the transform chain camera → body → NED and on who publishes it (Vision).
- **Timestamps / sync**: agree message timestamps so detection and vehicle state align for a moving target.

### Integration testbed

Gazebo is the **official integration testbed**: every interface above (I1–I13) must pass in simulation before being connected on hardware.

## 6. Phase scope, deliverable & V-diagram

This phase is the **requirements analysis** step of the V-diagram. Its deliverable is this formal description of the project and its organisation into departments.

![V-diagram](Pictures/v-diagram.png)

## 7. Open questions / TBD

- **Claw command path**: PX4 AUX PWM channel vs. companion/ROS 2 → servo driver. Not yet decided.
- **Quantitative targets**: payload, flight time, detection rate, grasp success rate, cycle time, alignment accuracy.
- **Environment and regulations**: operating environment, lighting, and applicable drone rules.
- **Mission manager**: final placement and ownership of the mission/state machine (future department).
