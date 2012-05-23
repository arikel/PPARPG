#!/usr/bin/python
# -*- coding: utf8 -*-

# config.py


K_FORWARD = "z"
K_BACKWARD = "s"
K_LEFT = "q"
K_RIGHT = "d"
K_TURN_LEFT = "a"
K_TURN_RIGHT = "e"
K_SHOOT = "mouse1"
K_DRAG = "mouse2"
K_JUMP = "mouse3"
K_CROUCH = "c"
K_ZOOM_IN = "wheel_up"
K_ZOOM_OUT = "wheel_down"
K_SWITCH = "tab"
K_OPEN = "space"
K_DROP = "f"

KEY_LIST = [K_FORWARD, K_BACKWARD,
	K_LEFT, K_RIGHT,
	K_TURN_LEFT, K_TURN_RIGHT,
	K_SHOOT, K_DRAG, K_JUMP, K_CROUCH,
	K_ZOOM_IN, K_ZOOM_OUT,
	K_SWITCH,
	K_OPEN,
	K_DROP
]

#-----------------------------------------------------------------------
# camera control
#-----------------------------------------------------------------------
FORWARD = "z"
BACKWARD = "s"
STRAFE_LEFT = "q"
STRAFE_RIGHT = "d"
TURN_LEFT = "a"
TURN_RIGHT = "e"
UP = "f"
DOWN = "c"

#-----------------------------------------------------------------------
# editor commands
#-----------------------------------------------------------------------
OPEN_EDITOR = "control-e"
SAVE = "control-s"
OPEN = "control-o"
CLEAR_COLLISION = "control-c"
FILL_COLLISION = "control-f"

GRAB = "g"
ROTATE = "r"
DESTROY = "x"
DUPLICATE = "shift-d"
EDITOR_UP = "arrow_up"
EDITOR_DOWN = "arrow_down"
EDITOR_LEFT = "arrow_left"
EDITOR_RIGHT = "arrow_right"

#-----------------------------------------------------------------------
# game commands
#-----------------------------------------------------------------------
INVENTORY = "i"

#-----------------------------------------------------------------------
# display settings
#-----------------------------------------------------------------------
#CONFIG_LIGHT = False
CONFIG_LIGHT = True
#CONFIG_W, CONFIG_H = 800, 600
CONFIG_W, CONFIG_H = 1024, 768
#CONFIG_W, CONFIG_H = 1280, 1024
#CONFIG_W, CONFIG_H = 1280, 960
CONFIG_FULLSCREEN = False




