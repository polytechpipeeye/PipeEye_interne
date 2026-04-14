# PipeEye

## Description du Projet
Le projet **PipeEye** a pour finalité de concevoir et de réaliser un système robotisé destiné à faciliter la maintenance et l'inspection de l’intérieur des tuyaux, particulièrement dans le domaine naval. 

Il consiste à concevoir, réaliser et intégrer une tourelle de caméra directionnelle (PAN/TILT) embarquée sur un robot mobile, associée à des outils de vision avancés (HUD dynamique, zoom progressif numérique) et d'éclairage (anneau LED Neopixel modulaire). Ce robot est destiné à inspecter des tuyaux en acier de 60 mm à 300 mm de diamètre, souvent inaccessibles à l’homme, afin de détecter des obstructions, des zones corrodées ou des intrusions d’objets.

## Environnement Technique
Le projet repose sur une architecture distribuée moderne :
* **Système d'exploitation :** Ubuntu 22.04 LTS
* **Middleware :** ROS 2 Iron
* **Ordinateur embarqué :** Raspberry Pi 4B
* **Interface Vidéo :** Web Video Server (HTTP)

## Composants Matériels
* **Caméra :** Caméra USB Haute Définition (1280x720p)
* **Éclairage :** Anneau NeoPixel 12 LEDs
* **Moteurs :** Micro Servo Motors 9g
* **Convertisseur DC-DC (12V -> 5V) :** DFR0571
* **Level Shifter (3.3V -> 5V) :** BOB12009
* **Interface de contrôle :** Manette Sony PS4 DualShock USB

##  Architecture du Projet
Le code source est organisé dans un workspace ROS 2 (`ros2_ws`) structuré de la manière suivante :


├── ros2_ws/
│   ├── hud_camera_cpp/           # Paquet C++ : Traitement d'image (Viseur, HUD, Zoom)
│   ├── my_robot_interface/       # Paquet de messages personnalisés (ex: LedControl.msg)
│   ├── my_servo_control/         # Paquet Python principal du robot
│   │   ├── launch/               # Fichiers de lancement (pipeeye.launch.py)
│   │   └── my_servo_control/     # Scripts Python (Manette, Moteurs, NeoPixel...)
│   ├── www/                      # Dossier contenant l'interface Web (index.html)
│   ├── run_robot.sh              # Script exécutable d'automatisation du lancement
└── README.md

## Installation et Lancement

Le lancement du système PipeEye dépend de votre configuration matérielle (lancement local ou contrôle à distance via Ethernet).

Option 1 : Lancement Local (Directement sur le robot)

Si vous avez un écran et la manette branchés directement sur la Raspberry Pi du robot, il vous suffit de vous placer dans l'espace de travail et d'exécuter le script principal :
cd ros2_ws
./run_robot.sh

(Le script se chargera de sourcer l'environnement et de lancer tous les nœuds ROS 2, y compris celui de la manette).


Option 2 : Lancement à Distance (Connexion Ethernet / Poste Opérateur)

C'est la configuration standard en conditions réelles. La manette est branchée sur le poste opérateur (seconde Raspberry Pi), qui communique avec le robot via un câble Ethernet.

Étape 1 : Préparation du fichier de lancement (Sur le robot)
Puisque la manette n'est plus branchée sur le robot, il faut indiquer à ROS 2 de ne pas chercher à la lire localement.

Connectez-vous au robot en SSH grâce au raccourci configuré :

Bash
ssh pipeeye
Ouvrez le fichier pipeeye.launch.py (situé dans my_servo_control/launch/) et mettez en commentaire le nœud correspondant à la manette.

Étape 2 : Lancement du système (Sur le robot)
Toujours depuis votre terminal SSH (pipeeye), lancez le script d'automatisation :


cd ros2_ws
./run_robot.sh

Étape 3 : Lancement du contrôle (Sur le poste opérateur)
Ouvrez un nouveau terminal local sur votre poste opérateur (celui où la manette est branchée) et lancez l'écoute de la manette via l'alias préconfiguré : manette

Le système est désormais en ligne ! Vous pouvez ouvrir votre navigateur et vous rendre sur http://10.10.10.1:8081 pour avoir l'interface vidéo pour commencer l'inspection.

Le package manette_pkg et le package contenant les fichier permettant de controler la manette, il est à mettre sur le poste operateur 
