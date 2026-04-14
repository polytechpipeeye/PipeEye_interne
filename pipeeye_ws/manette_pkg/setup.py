from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'manette_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name,'launch'), glob('launch/*.launch.py')),
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
        'manette=manette_pkg.manette:main',
        'screenshot_node=manette_pkg.screenshot_node:main'
        ],
    },
)
