from config import messages, is_debug
from robot import Robot

if __name__ == "__main__":
    Robot(plugin=plugin, messages=messages, is_debug=is_debug).on()