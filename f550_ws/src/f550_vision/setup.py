from glob import glob

from setuptools import find_packages, setup


setup(
    name='f550_vision',
    version='0.2.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/f550_vision']),
        ('share/f550_vision', ['package.xml', 'README.md']),
        ('share/f550_vision/launch', glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ClawDrone maintainers',
    maintainer_email='mapy7772004@gmail.com',
    description="Downward camera bridge, viewer and YOLO detector for ClawDrone's F550.",
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_viewer = f550_vision.camera_viewer_node:main',
            'ball_detector = f550_vision.ball_detector_node:main',
        ],
    },
)
