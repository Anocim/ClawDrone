import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleCommand
from std_msgs.msg import Bool

class SafetyNode(Node):
    def __init__(self):
        super().__init__('safety_node')
        
        # Publicador de comandos hacia PX4
        self.publisher_vehicle_command = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        # Suscriptor al botón de pánico de ROS 2
        self.subscription = self.create_subscription(Bool, '/emergency_override', self.emergency_callback, 10)
        
        self.get_logger().info('Nodo de seguridad activo. Escuchando en /emergency_override')

    def emergency_callback(self, msg):
        if msg.data:
            self.get_logger().warn('¡EMERGENCIA! Abortando autonomía. Pasando a modo POSICIÓN (Manual).')
            
            # param1=1.0 (Custom mode), param2=3.0 (Position mode)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=3.0)
            
            # Si en su lugar quisieras que aterrizara automáticamente, usarías:
            # self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)

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
    rclpy.init(args=args)
    node = SafetyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
