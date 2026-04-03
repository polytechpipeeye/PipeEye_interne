import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # --- CONFIGURATION DES NŒUDS ---

    # 1. Le Cerveau : Publisher de la manette
    joy_pub = Node(
        package='my_servo_control',
        executable='right_stick_publisher',
        name='joy_pub',
        output='screen',
        arguments=['--log-level', 'warn']
    )

    # 2. Les Servos (S'abonne au mouvement)
    servo_sub = Node(
        package='my_servo_control',
        executable='subscriber_servo_xy',
        name='servo_sub',
        #remappings=[('/topic', 'right_stick')], 
        output='screen',
        arguments=['--log-level', 'warn']
    )

    # 3. Les LEDs (S'abonne aux boutons)
    led_sub = Node(
        package='my_servo_control',
        executable='neopixel_test',
        name='led_sub',
        #remappings=[('/topic', 'LEDinput')],
        output='screen',
        arguments=['--log-level', 'warn']
    )

    # 4. Listener de debug (si tu veux voir les coordonnées passer)
    joy_listener = Node(
        package='my_servo_control',
        executable='right_stick_listener',
        name='joy_debug',
        #remappings=[('/topic', 'right_stick')],
        output='screen',
        arguments=['--log-level', 'warn']
    )

    # 5. Autres nœuds utilitaires (en mode silencieux 'log')
    '''others = [
        Node(package='my_servo_control', executable='camera_node', name='camera', output='log'),
        Node(package='my_servo_control', executable='veltopwm', name='veltopwm', output='log'),
        Node(package='my_servo_control', executable='maxon', name='maxon', output='log'),
        Node(package='my_servo_control', executable='realsense', name='realsense', output='log'),
        Node(package='my_servo_control', executable='sub', name='sub_generic', output='log'),
        Node(package='my_servo_control', executable='talker', name='controller_main', output='log'),
    ]
'''
    # --- ASSEMBLAGE ---
    return LaunchDescription([
        #joy_pub,
        servo_sub,
        led_sub,
        joy_listener,
        #*others
    ])
