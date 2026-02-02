is_debug = True

robot_name = "Robot"

messages = {
    "on_join": "Hello {}!",
    "hi": "Hello {}!",
    "prefix": "{}: ".format(robot_name),
}

# Was trying to do it modular but not enough time. Improvising...
enabled_commands = [
    "tp",
    "hi",
    "die"
]