from setuptools import find_packages, setup


setup(
    name='f550_monitor',
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/f550_monitor']),
        ('share/f550_monitor', ['package.xml', 'README.md']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ClawDrone maintainers',
    maintainer_email='mapy7772004@gmail.com',
    description='Read-only local PX4 odometry monitoring for ClawDrone.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'telemetry_monitor = f550_monitor.telemetry_monitor_node:main',
        ],
    },
)
