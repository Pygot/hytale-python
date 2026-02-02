from config import messages, is_debug, enabled_commands
from robot import Robot

if __name__ == "__main__":
    Robot(
        plugin=plugin,
        messages=messages,
        enabled_cmds=enabled_commands,
        is_debug=is_debug
    ).on()