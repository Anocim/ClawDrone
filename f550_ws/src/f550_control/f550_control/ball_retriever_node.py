import math
import queue
import sys
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLandDetected,
    VehicleLocalPosition,
    VehicleOdometry,
    VehicleStatus,
)


class BallRetrieverNode(Node):
    TIMER_PERIOD = 0.1
    HORIZONTAL_SPEED = 0.6  # m/s
    VERTICAL_SPEED = 0.25  # m/s
    XY_TOLERANCE = 0.3  # m
    Z_TOLERANCE = 0.2  # m
    PICKUP_PAUSE_TICKS = 50  # 5 seconds at 10 Hz
    DROP_PAUSE_TICKS = 50

    def __init__(self, ball_coords, drop_coords):
        super().__init__('ball_retriever_node')

        self.publisher_offboard_mode = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.publisher_trajectory = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.publisher_vehicle_command = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', 10)

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.position_subscriptions = [
            self.create_subscription(
                VehicleLocalPosition,
                topic,
                self.position_callback,
                px4_qos,
            )
            for topic in (
                '/fmu/out/vehicle_local_position',
                '/fmu/out/vehicle_local_position_v1',
            )
        ]
        self.odometry_subscription = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odometry_callback,
            px4_qos,
        )
        self.land_subscription = self.create_subscription(
            VehicleLandDetected,
            '/fmu/out/vehicle_land_detected',
            self.land_callback,
            px4_qos,
        )
        self.status_subscription = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.status_callback,
            px4_qos,
        )

        self.current_pos = [0.0, 0.0, 0.0]
        self.commanded_position = [0.0, 0.0, 0.0]
        self.position_received = False
        self.position_wait_counter = 0
        self.armed = None
        self.status_received = False
        self.nav_state = None
        self.landed = False
        self.has_taken_off = False

        self.ball_coords = ball_coords
        self.drop_coords = drop_coords
        self.target_position = [0.0, 0.0, -5.0]
        self.state = 'TAKEOFF'
        self.wait_counter = 0
        self.counter = 0
        self.landing_counter = 0
        self.disarm_counter = 0
        self.last_setpoint_update = time.monotonic()

        self.mission_queue = queue.Queue()
        self.new_mission_event = threading.Event()

        self.timer = self.create_timer(self.TIMER_PERIOD, self.timer_callback)
        self.get_logger().info(
            'Misión iniciada. Setpoints limitados a 0.6 m/s en horizontal '
            'y 0.25 m/s en vertical.')

    def update_position(self, x, y, z, source):
        self.current_pos = [x, y, z]
        if not self.position_received:
            self.get_logger().info(
                f'Posición PX4 recibida ({source}): '
                f'[{x:.2f}, {y:.2f}, {z:.2f}] m')
        self.position_received = True

    def position_callback(self, msg):
        self.update_position(msg.x, msg.y, msg.z, 'vehicle_local_position')

    def odometry_callback(self, msg):
        if msg.pose_frame != VehicleOdometry.POSE_FRAME_NED:
            return
        if not all(math.isfinite(value) for value in msg.position):
            return
        self.update_position(*msg.position, 'vehicle_odometry')

    def land_callback(self, msg):
        self.landed = msg.landed
        if not msg.landed:
            self.has_taken_off = True

    def status_callback(self, msg):
        self.armed = msg.arming_state == VehicleStatus.ARMING_STATE_ARMED
        self.status_received = True
        self.nav_state = msg.nav_state

    def distance_to_target(self):
        dx = self.current_pos[0] - self.target_position[0]
        dy = self.current_pos[1] - self.target_position[1]
        dz = self.current_pos[2] - self.target_position[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def target_reached(self):
        dx = self.current_pos[0] - self.target_position[0]
        dy = self.current_pos[1] - self.target_position[1]
        dz = self.current_pos[2] - self.target_position[2]
        return (math.hypot(dx, dy) <= self.XY_TOLERANCE
                and abs(dz) <= self.Z_TOLERANCE)

    def publish_offboard_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = self.timestamp_us()
        self.publisher_offboard_mode.publish(msg)

    def publish_trajectory(self):
        msg = TrajectorySetpoint()
        msg.position = self.commanded_position
        msg.yaw = 0.0
        msg.timestamp = self.timestamp_us()
        self.publisher_trajectory.publish(msg)

    def timestamp_us(self):
        return int(self.get_clock().now().nanoseconds / 1000)

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.param1 = param1
        msg.param2 = param2
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = self.timestamp_us()
        self.publisher_vehicle_command.publish(msg)

    def advance_commanded_position(self):
        now = time.monotonic()
        dt = min(max(now - self.last_setpoint_update, 0.0), 0.2)
        self.last_setpoint_update = now

        dx = self.target_position[0] - self.commanded_position[0]
        dy = self.target_position[1] - self.commanded_position[1]
        horizontal_distance = math.hypot(dx, dy)
        horizontal_step = self.HORIZONTAL_SPEED * dt
        if horizontal_distance <= horizontal_step:
            self.commanded_position[0] = self.target_position[0]
            self.commanded_position[1] = self.target_position[1]
        elif horizontal_distance > 0.0:
            scale = horizontal_step / horizontal_distance
            self.commanded_position[0] += dx * scale
            self.commanded_position[1] += dy * scale

        dz = self.target_position[2] - self.commanded_position[2]
        vertical_step = self.VERTICAL_SPEED * dt
        self.commanded_position[2] += max(-vertical_step, min(vertical_step, dz))

    def start_next_mission(self):
        try:
            ball_coords, drop_coords = self.mission_queue.get_nowait()
        except queue.Empty:
            return False

        self.ball_coords = ball_coords
        self.drop_coords = drop_coords
        self.state = 'TAKEOFF'
        self.target_position = [0.0, 0.0, -5.0]
        self.commanded_position = list(self.current_pos)
        self.counter = 0
        self.wait_counter = 0
        self.has_taken_off = False
        self.landing_counter = 0
        self.disarm_counter = 0
        self.last_setpoint_update = time.monotonic()
        self.get_logger().info('Nueva misión iniciada.')
        return True

    def landing_callback_cycle(self):
        if self.has_taken_off and self.landed:
            if self.status_received and not self.armed:
                self.state = 'WAIT_MISSION'
                self.get_logger().info(
                    'Aterrizaje y desarmado confirmados. Preparado para otra misión.')
                self.new_mission_event.set()
                return

            if self.status_received and self.armed and self.disarm_counter % 10 == 0:
                self.publish_vehicle_command(
                    VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM,
                    param1=0.0,
                )
            self.disarm_counter += 1
            return

        if (self.status_received
                and self.nav_state == VehicleStatus.NAVIGATION_STATE_AUTO_LAND):
            return

        # Mantén Offboard activo hasta que PX4 confirme Auto Land; esto evita
        # perder el control externo si el primer comando de aterrizaje se retrasa.
        self.publish_offboard_mode()
        self.publish_trajectory()
        if self.landing_counter % 10 == 0:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
        self.landing_counter += 1

    def timer_callback(self):
        if self.state == 'WAIT_MISSION':
            self.start_next_mission()
            return
        if self.state == 'LANDING':
            self.landing_callback_cycle()
            return

        self.publish_offboard_mode()
        self.advance_commanded_position()
        distance = self.distance_to_target()

        if self.counter % 10 == 0:
            self.get_logger().info(
                f'[{self.state}] Obj: {self.target_position} | '
                f'Real: [{self.current_pos[0]:.1f}, {self.current_pos[1]:.1f}, '
                f'{self.current_pos[2]:.1f}] | Dist: {distance:.2f} m')

        if not self.position_received and self.position_wait_counter % 20 == 0:
            topic_counts = {
                topic: self.count_publishers(topic)
                for topic in (
                    '/fmu/out/vehicle_local_position',
                    '/fmu/out/vehicle_local_position_v1',
                    '/fmu/out/vehicle_odometry',
                )
            }
            self.get_logger().warning(
                f'Sin posición local de PX4; publicadores detectados: {topic_counts}')
        if not self.position_received:
            self.position_wait_counter += 1

        if self.state == 'TAKEOFF':
            if self.target_reached():
                self.state = 'APPROACH_BALL'
                self.target_position = [self.ball_coords[0], self.ball_coords[1], -5.0]
                self.get_logger().info('Altura de tránsito alcanzada. Yendo sobre la pelota.')

        elif self.state == 'APPROACH_BALL':
            if self.target_reached():
                self.state = 'DESCEND_BALL'
                self.target_position = list(self.ball_coords)
                self.get_logger().info('Sobre la coordenada de la pelota. Descendiendo despacio.')

        elif self.state == 'DESCEND_BALL':
            if self.target_reached():
                self.state = 'GRAB'
                self.wait_counter = self.PICKUP_PAUSE_TICKS
                self.get_logger().warning(
                    'Llegó al punto de recogida. No hay sensor ni pinza controlada: '
                    'la captura NO está confirmada. Pausa de 5 s.')

        elif self.state == 'GRAB':
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.state = 'ASCEND'
                self.target_position = [self.ball_coords[0], self.ball_coords[1], -5.0]
                self.get_logger().info(
                    'Pausa terminada; continúo sin confirmar captura. Ascendiendo.')

        elif self.state == 'ASCEND':
            if self.target_reached():
                self.state = 'GOTO_DROP'
                self.target_position = [self.drop_coords[0], self.drop_coords[1], -5.0]
                self.get_logger().info('Altura de tránsito alcanzada. Yendo a entrega.')

        elif self.state == 'GOTO_DROP':
            if self.target_reached():
                self.state = 'DESCEND_DROP'
                self.target_position = list(self.drop_coords)
                self.get_logger().info('Sobre la zona de entrega. Descendiendo despacio.')

        elif self.state == 'DESCEND_DROP':
            if self.target_reached():
                self.state = 'DROP'
                self.wait_counter = self.DROP_PAUSE_TICKS
                self.get_logger().warning(
                    'Llegó a la coordenada de entrega. No hay mecanismo de liberación '
                    'controlado; la entrega NO está confirmada. Pausa de 5 s.')

        elif self.state == 'DROP':
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.state = 'RTL'
                self.target_position = [0.0, 0.0, -5.0]
                self.get_logger().info('Pausa terminada. Regresando al origen.')

        elif self.state == 'RTL':
            if self.target_reached():
                self.state = 'LANDING'
                self.landing_counter = 0
                self.disarm_counter = 0
                self.get_logger().info('Origen alcanzado. Solicitando aterrizaje.')
                self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
                return

        self.publish_trajectory()

        if 10 <= self.counter < 30:
            self.publish_vehicle_command(
                VehicleCommand.VEHICLE_CMD_DO_SET_MODE,
                param1=1.0,
                param2=6.0,
            )
            self.publish_vehicle_command(
                VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM,
                param1=1.0,
            )
        if self.counter < 35:
            self.counter += 1


def read_mission_coordinates():
    print('Introduce X/Y del mundo Gazebo ENU: X=Este, Y=Norte.')
    print('Z se introduce en NED (positivo hacia abajo; suelo cerca de 0).')
    ball_x = float(input(' [Pelota] X (Este / mundo Gazebo): '))
    ball_y = float(input(' [Pelota] Y (Norte / mundo Gazebo): '))
    ball_z = float(input(' [Pelota] Z (NED, abajo positivo): '))
    drop_x = float(input(' [Entrega] X (Este / mundo Gazebo): '))
    drop_y = float(input(' [Entrega] Y (Norte / mundo Gazebo): '))
    drop_z = float(input(' [Entrega] Z (NED, abajo positivo): '))
    values = [ball_x, ball_y, ball_z, drop_x, drop_y, drop_z]
    if not all(math.isfinite(value) for value in values):
        raise ValueError('Las coordenadas deben ser números finitos.')
    # Gazebo's world is ENU while PX4's trajectory setpoints use NED:
    # north = Gazebo Y and east = Gazebo X.
    return [ball_y, ball_x, ball_z], [drop_y, drop_x, drop_z]


def read_next_mission(node):
    while rclpy.ok():
        if not node.new_mission_event.wait(timeout=0.5):
            continue
        node.new_mission_event.clear()
        if not rclpy.ok():
            return
        print('\nAterrizaje terminado. Introduce las coordenadas de la siguiente misión.')
        try:
            ball_coords, drop_coords = read_mission_coordinates()
        except (ValueError, EOFError) as error:
            print(f'Coordenadas no válidas: {error}. Se volverán a pedir.')
            node.new_mission_event.set()
            continue
        node.mission_queue.put((ball_coords, drop_coords))
        print('Misión preparada; comenzará cuando el nodo procese las coordenadas.')


def main(args=None):
    print('\n' + '=' * 50)
    print(' INICIALIZACIÓN DE MISIÓN AUTÓNOMA F550')
    print('=' * 50)
    try:
        ball_coords, drop_coords = read_mission_coordinates()
    except (ValueError, EOFError) as error:
        print(f'ERROR: {error}')
        sys.exit(1)

    rclpy.init(args=args)
    node = BallRetrieverNode(ball_coords, drop_coords)
    input_thread = threading.Thread(
        target=read_next_mission,
        args=(node,),
        daemon=True,
    )
    input_thread.start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
