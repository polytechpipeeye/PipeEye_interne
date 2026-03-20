from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'my_servo_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[py]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pipeeye',
    maintainer_email='pipeeye@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	#'camera_node = my_servo_control.camera_node:main',
        	'neopixel_test = my_servo_control.neopixel_test:main',
        	'right_stick_publisher = my_servo_control.right_stick_publisher:main',
		'right_stick_listener = my_servo_control.right_stick_listener:main',
		#'talker = my_servo_control.controller:main',
         	#'veltopwm = my_servo_control.veltopwm:main',
         	#'sub = my_servo_control.sub:main',
         	#'maxon = my_servo_control.maxon:main',
         	#'realsense = my_servo_control.realsense:main',
         	'subscriber_servo_xy=my_servo_control.subscriber_servo_xy:main',
        ],
    },
)
