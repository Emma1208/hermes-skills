#!/bin/bash
# Termux:Boot — demarre le watchdog Hermes de facon COMPLETEMENT detachee
# (sa propre session / process group) pour qu'il survive a un crash du gateway.
# Ce script tourne au boot du telephone, HORS de l'arbre du gateway Hermes,
# donc il n'est pas touche par la protection anti-auto-kill du gateway.
#
# Install : copier dans ~/.termux/boot/ et rendre executable
#   cp termux-boot-hermes.sh ~/.termux/boot/start-hermes-watchdog.sh
#   chmod +x ~/.termux/boot/start-hermes-watchdog.sh
# (Termux:Boot doit etre installe et autorise au demarrage)

command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock
setsid nohup bash /root/hermes-guard/watchdog.sh >/dev/null 2>&1 &
