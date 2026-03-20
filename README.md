# PipeEye_interne

## Description du Projet
Le projet PipeEye a pour finalité de concevoir et de réaliser un système robotisé destiné à faciliter la maintenance de l’intérieur des tuyaux dans le domaine naval.
Celui-ci consiste à concevoir, réaliser et intégrer une caméra (PAN/TILT) embarquée sur un robot mobile déjà conçu, associée à des outils complémentaires (anneau LED, profilomètre). Ce robot est destiné à inspecter des tuyaux en acier de 60 mm à 300 mm de diamètre, souvent inaccessibles à l’homme, afin de détecter des obstructions, zones corrodées ou intrusions d’objets.

## Environnement utilisé
Le projet s'intègre sur le middleware ROS2 Iron dans un environnement Ubuntu 22.04 et le tout modulé sur une carte Raspberry Pi 4B.

## Composants utilisés
Anneau LED : Neopixel Ring 12 LEDs\
Moteurs : Micro Servo Motors 9g 360deg\
Convertisseur DC-DC (12V -> 5V) : DFR0571\
Level Shifter (3.3V -> 5V) : BOB12009\
Camera : Caméra 8 Mpx CAM-JT-V2-77\
Manette de contrôle: PS4 Dualshock

## Compilation et lancement du projet
```bash
./run_robot.sh
```

## Manipulations sur la manette PS4
**Anneau LED :** \
*Quart de l'anneau :* boutons d'orientation à gauche\ 
*Intensité lumineuse :* bouton R1\

**Moteurs :** \
*Moteur PAN :* joystick à la droite\
*Moteur TILT :* joystick à la gauche\
*Vitesse :* bouton triangle


