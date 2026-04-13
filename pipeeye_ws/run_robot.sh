#!/bin/bash
cd ~/ros2_ws

cleanup() {
    echo ""
    echo " Arrêt de tous les composants..."
    sudo killall -9 camera_node 2>/dev/null
    sudo killall -9 web_video_server 2>/dev/null
    sudo killall -9 hud_node 2>/dev/null
    pkill -f "python3 -m http.server" 2>/dev/null
    pkill -f "ros2 launch my_servo_control" 2>/dev/null
    echo " PipeEye désactivé."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo "Compilation de tous les packages (Interface + Servo + Caméra)..."
source /opt/ros/iron/setup.bash
colcon build --symlink-install

if [ $? -ne 0 ]; then
    echo "Erreur de compilation ! Vérifie tes packages."
    exit 1
fi

echo "Compilation réussie."
source install/setup.bash

echo "Lancement de Pipeeye..."
ros2 run v4l2_camera v4l2_camera_node --ros-args -p video_device:="/dev/video0" -p image_size:="[1280,780]" --remap image_raw:=/camera/image_raw &
sudo -E env "PATH=$PATH" "PYTHONPATH=$PYTHONPATH" "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" \
ros2 launch my_servo_control pipeeye.launch.py & 
sleep 10
ros2 run hud_camera_cpp hud_node &
ros2 run web_video_server web_video_server & 
python3 -m http.server 8081 -d /home/mathis/ros2_ws/www & 
IP_PI=$(hostname -I | awk '{print $1}')
echo "Pipeye est en ligne"
echo "Allez à l'adresse http://$IP_PI:8081"
wait
