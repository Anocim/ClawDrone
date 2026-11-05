import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand
import threading
import sys
import termios
import tty
import time
import os

class OffboardHybridControl(Node):
    def __init__(self):
        super().__init__('offboard_hybrid_control')
        
        self.publisher_offboard_mode = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.publisher_trajectory = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.publisher_vehicle_command = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        self.target_position = [0.0, 0.0, -5.0]
        self.target_yaw = 0.0
        
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.counter = 0

        self.input_thread = threading.Thread(target=self.read_keyboard, daemon=True)
        self.input_thread.start()

    def timer_callback(self):
        msg_mode = OffboardControlMode()
        msg_mode.position = True
        msg_mode.velocity = False
        msg_mode.acceleration = False
        msg_mode.attitude = False
        msg_mode.body_rate = False
        msg_mode.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_offboard_mode.publish(msg_mode)

        msg_traj = TrajectorySetpoint()
        msg_traj.position = self.target_position
        msg_traj.yaw = self.target_yaw
        msg_traj.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.publisher_trajectory.publish(msg_traj)

        if self.counter >= 10 and self.counter < 30:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, param1=1.0, param2=6.0)
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
            
        if self.counter < 35:
            self.counter += 1

    def read_keyboard(self):
        time.sleep(4)
        print("\n" + "="*60)
        print(" CONTROL HÍBRIDO F550 (Flechas + Coordenadas)")
        print(" Flecha Arriba / Abajo    : Avanzar / Retroceder (X +/- 0.5m)")
        print(" Flecha Derecha / Izq     : Derecha / Izquierda  (Y +/- 0.5m)")
        print(" Tecla 'w' / 's'          : Subir / Bajar Altitud")
        print(" Tecla 'c'                : INTRODUCIR COORDENADAS EXACTAS (X Y Z)")
        print(" Tecla 'q'                : Salir")
        print("="*60 + "\n")

        settings = termios.tcgetattr(sys.stdin)
        step = 0.5

        try:
            while rclpy.ok():
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
                
                if key == '\x1b':
                    key += sys.stdin.read(2)
                
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
                
                if key == '\x1b[A':    # Flecha Arriba
                    self.target_position[0] += step
                elif key == '\x1b[B':  # Flecha Abajo
                    self.target_position[0] -= step
                elif key == '\x1b[C':  # Flecha Derecha
                    self.target_position[1] += step
                elif key == '\x1b[D':  # Flecha Izquierda
                    self.target_position[1] -= step
                elif key == 'w':       # Subir
                    self.target_position[2] -= step
                elif key == 's':       # Bajar
                    self.target_position[2] += step
                elif key == 'c':       # MODO INTRODUCIR COORDENADAS PRECISAS
                    print("\n\n" + "-"*40)
                    try:
                        user_input = input("Introduce X Y Z (ej: 15.0 -8.0 -10.0): ")
                        coords = [float(val) for val in user_input.strip().split()]
                        if len(coords) == 3:
                            self.target_position = coords
                            print(f"--> Nuevo objetivo asignado: X={coords[0]}, Y={coords[1]}, Z={coords[2]}")
                        else:
                            print(" [!] Error: Introduce 3 valores (X Y Z).")
                    except Exception as e:
                        print(f" [!] Entrada no válida: {e}")
                    print("-"*40 + "\nVolviendo a control por teclado...\n")
                elif key == 'q' or key == '\x03':
                    break
                
                sys.stdout.write(f"\r--> Objetivo actual: X={self.target_position[0]:.1f}, Y={self.target_position[1]:.1f}, Z={self.target_position[2]:.1f}   ")
                sys.stdout.flush()
                
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
            print("\nSaliendo del control...")
            os._exit(0)

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
    node = OffboardHybridControl()
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