#!/bin/bash
cd ~/ros2_ws

echo "Compilation de tous les packages (Interface + Servo)..."
colcon build --symlink-install

if [ $? -ne 0 ]; then
    echo "Erreur de compilation ! Vérifie tes packages."
    exit 1
fi

echo "Compilation réussie."
source install/setup.bash

echo "Lancement de Pipeeye..."
sudo -E env "PATH=$PATH" "PYTHONPATH=$PYTHONPATH" "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" \
ros2 launch my_servo_control pipeeye.launch.py
