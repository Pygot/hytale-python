# type: ignore

from java.util.logging import Level

from defaults import prefix


def info(hytaleLogger, message):
    hytaleLogger.at(Level.INFO).log(prefix + message)
    return True


def error(hytaleLogger, message):
    hytaleLogger.at(Level.SEVERE).log(prefix + message)
    return True


def debug(hytaleLogger, message, is_debug):
    if is_debug:
        hytaleLogger.at(Level.INFO).log("[DEBUG] " + prefix + message)
    return is_debug