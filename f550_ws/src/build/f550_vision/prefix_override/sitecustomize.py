import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/alejandro/ClawDrone/ClawDrone/f550_ws/src/install/f550_vision'
