import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleLocalPosition
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
import math
import sys

class BallRetrieverNode(Node):
    def __init__(self, ball_coords, drop_coords):
        super().__init__('ball_retriever_node')
        
        self.publisher_offboard_mode = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.publisher_trajectory = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.publisher_vehicle_command = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        # QoS EXACTO para puente DDS de PX4
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.subscription = self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position_v1',
            self.position_callback,
            qos_profile)
            
        self.current_pos = [0.0, 0.0, 0.0]
        self.ball_coords = ball_coords
        self.drop_coords = drop_coords
        
        self.state = 'TAKEOFF'
        self.target_position = [0.0, 0.0, -5.0]
        self.wait_counter = 0
        self.counter = 0
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Iniciando Misión: Fase TAKEOFF')

    def position_callback(self, msg):
        self.current_pos = [msg.x, msg.y, msg.z]

    def distance_to_target(self):
        return math.sqrt(
            (self.current_pos[0] - self.target_position[0])**2 +
            (self.current_pos[1] - self.target_position[1])**2 +
            (self.current_pos[2] - self.target_position[2])**2
        )

    def timer_callback(self):
        msg_mode = OffboardControlMode()
        msg_mode.position = True
        msg_mode.velocity = False
        msg_mode.acceleration = False
        msg_mode.attitude = False
        msg_mode.body_rate = False
        msg_mode.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_offboard_mode.publish(msg_mode)

        dist = self.distance_to_target()
        
        if self.counter % 10 == 0:
            self.get_logger().info(f'[{self.state}] Obj: {self.target_position} | Real: [{self.current_pos[0]:.1f}, {self.current_pos[1]:.1f}, {self.current_pos[2]:.1f}] | Dist: {dist:.2f}m')

        TOLERANCE = 0.8
        
        if self.state == 'TAKEOFF':
            if dist < TOLERANCE:
                self.state = 'APPROACH_BALL'
                self.target_position = [self.ball_coords[0], self.ball_coords[1], -5.0]
                self.get_logger().info('Despegue completado. Yendo sobre la pelota.')
                
        elif self.state == 'APPROACH_BALL':
            if dist < TOLERANCE:
                self.state = 'DESCEND_BALL'
                self.target_position = self.ball_coords
                self.get_logger().info('Sobre la pelota. Descendiendo.')
                
        elif self.state == 'DESCEND_BALL':
            if dist < TOLERANCE:
                self.state = 'GRAB'
                self.wait_counter = 30
                self.get_logger().info('PELOTA DETECTADA. Activando pinzas (esperando 3s)...')
                
        elif self.state == 'GRAB':
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.state = 'ASCEND'
                self.target_position = [self.ball_coords[0], self.ball_coords[1], -5.0]
                self.get_logger().info('Pelota asegurada. Ascendiendo.')
                
        elif self.state == 'ASCEND':
            if dist < TOLERANCE:
                self.state = 'GOTO_DROP'
                self.target_position = [self.drop_coords[0], self.drop_coords[1], -5.0]
                self.get_logger().info('Ascenso completado. Yendo a zona de entrega.')
                
        elif self.state == 'GOTO_DROP':
            if dist < TOLERANCE:
                self.state = 'DESCEND_DROP'
                self.target_position = self.drop_coords
                self.get_logger().info('Sobre zona de entrega. Descendiendo.')
                
        elif self.state == 'DESCEND_DROP':
            if dist < TOLERANCE:
                self.state = 'DROP'
                self.wait_counter = 30
                self.get_logger().info('ZONA ALCANZADA. Soltando pelota (esperando 3s)...')
                
        elif self.state == 'DROP':
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.state = 'RTL'
                self.target_position = [0.0, 0.0, -5.0]
                self.get_logger().info('Pelota entregada. Retornando.')

        elif self.state == 'RTL':
            if dist < TOLERANCE:
                self.state = 'LAND'
                self.get_logger().info('Origen alcanzado. Aterrizando.')
                self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)

        msg_traj = TrajectorySetpoint()
        msg_traj.position = self.target_position
        msg_traj.yaw = 0.0
        msg_traj.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_trajectory.publish(msg_traj)

        if self.counter >= 10 and self.counter < 30:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
        
        if self.counter < 35:
            self.counter += 1

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
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_vehicle_command.publish(msg)

def main(args=None):
    print("\n" + "="*50)
    print(" INICIALIZACIÓN DE MISIÓN AUTÓNOMA F550")
    print(" (Usa formato decimal. Ej: 15.0. Z es negativo hacia arriba)")
    print("="*50)
    
    try:
        bx = float(input(" [Pelota] Coordenada X (Norte): "))
        by = float(input(" [Pelota] Coordenada Y (Este) : "))
        bz = float(input(" [Pelota] Altura Z (Ej: 0.0 o -0.5 para cogerla): "))
        
        print("-" * 50)
        dx = float(input(" [Entrega] Coordenada X (Norte): "))
        dy = float(input(" [Entrega] Coordenada Y (Este) : "))
        dz = float(input(" [Entrega] Altura Z (Ej: 0.0 para dejarla en el suelo): "))
    except ValueError:
        print("\n [!] ERROR: Debes introducir valores numéricos válidos.")
        sys.exit(1)

    rclpy.init(args=args)
    node = BallRetrieverNode([bx, by, bz], [dx, dy, dz])
    
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
