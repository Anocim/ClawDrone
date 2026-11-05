from setuptools import find_packages, setup

package_name = 'f550_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mapy',
    maintainer_email='mapy@todo.todo',
    description='Control offboard F550',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'offboard_node = f550_control.offboard_node:main',
            'safety_node = f550_control.safety_node:main',
            'ball_retriever_node = f550_control.ball_retriever_node:main'
        ],
    },
)
