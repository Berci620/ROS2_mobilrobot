import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ros2_course'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    # Include all launch files.
    (os.path.join('share', package_name),
        glob('launch/*launch.[pxy][yma]*'))
],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='berci',
    maintainer_email='berci@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'turtlebot_controller = ros2_course.turtlebot_controller:main',
            'turtlebot_closest_point = ros2_course.turtlebot_closest_point:main',
        ],
    },
)
