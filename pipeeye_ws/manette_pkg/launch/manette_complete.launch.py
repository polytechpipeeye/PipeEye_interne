from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
	return LaunchDescription([
		Node(
			package='joy',
			executable='joy_node',
			name='joy_node'
			
		),
		Node(
			package='manette_pkg',
			executable='manette',
			name='manette',
			output='screen'
		),
		Node(
			package='manette_pkg',
			executable='screenshot_node',
			name='screenshot_node',
			output='screen'
		)
	])
