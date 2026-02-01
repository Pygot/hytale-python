# Java imports
from com.hypixel.hytale.server.core.event.events.player import (
    PlayerReadyEvent,
    PlayerDisconnectEvent
)
from com.hypixel.hytale.server.npc import NPCPlugin
from com.hypixel.hytale.math.vector import Vector3f
from com.hypixel.hytale.server.core import Message
from java.io import File, FileReader, FileWriter
from com.google.gson import Gson
from java.util import Map

# Python imports
from pygot.entity import get_position, get_rotation
from pygot.world import get_world_by_name
from pygot.events import register_global
from datetime import datetime
from pygot.log import Log

import threading, time, os


class Robot:
    def __init__(
            self,
            plugin,
            messages,
            robot_name="Robot",
            default_world="default",
            storage_dir="players_storage/",
            is_debug=False
    ):
        # Robot
        self.default_world = default_world
        self.storage_dir = storage_dir
        self.robot_name = robot_name
        self.log = Log(plugin.Log)
        self.is_debug = is_debug
        self.messages = messages
        self.robot_ref = None
        self.plugin = plugin
        self.gson = Gson()
        self.rot_yaw = 0.0
        self.rot_y = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        # Players
        self.player_x = {}
        self.player_y = {}
        self.player_z = {}
        self.last_online = {}
        self.player_rot_yaw = {}
        self.player_rot_pitch = {}
        self.player_world = {}

    def on_join(self, event):
        player = event.getPlayer()
        player_ref = player.getReference()
        player_name = player.getDisplayName()

        self.last_online[player_name] = datetime.now().isoformat()

        position = get_position(player_ref, player_ref.getStore())
        rotation = get_rotation(player_ref, player_ref.getStore())

        # Position
        if position:
            self.log.debug("Updating position of robot & {}".format(player_name), self.is_debug)
            x, y, z = position.x, position.y, position.z
            self.player_x[player_name], self.x = x, x
            self.player_y[player_name], self.y = y, y
            self.player_z[player_name], self.z = z, z
        else:
            self.log.debug(
                "Cannot update position for robot & {}! Position not found...".format(player_name), self.is_debug
            )

        # Rotation
        if rotation:
            self.log.debug("Updating rotation of robot & {}".format(player_name), self.is_debug)
            x, y = rotation.x, rotation.y
            self.player_rot_yaw[player_name], self.rot_yaw = x, x
            self.player_rot_pitch[player_name], self.rot_y = y, y
        else:
            self.log.debug(
                "Cannot update rotation for robot & {}! Rotation not found...".format(player_name), self.is_debug
            )

        player.sendMessage(
            Message.raw(
                self.messages["prefix"] +
                self.messages["on_join"].format(player.getDisplayName())
            )
        )

        self.player_world[player_name] = get_world_by_name("default")

    def on_leave(self):  # TODO
        ...

    def load_storage(self, player_name):
        file_name = self.storage_dir + player_name.lower().capitalize() + ".json"

        file_obj = File(file_name)
        if not file_obj.exists():
            self.log.error("No {} found! Creating...".format(file_name))
            last_online = datetime.now().isoformat()
            default_data = {
                "last_online": last_online
            }
            writer = FileWriter(file_obj)
            writer.write(self.gson.toJson(default_data))
            writer.close()
            self.last_online[player_name] = last_online
            return

        try:
            reader = FileReader(file_obj)
            data = self.gson.fromJson(reader, Map)
            self.last_online[player_name] = data["last_online"]
            reader.close()
        except Exception as e:
            self.log.debug(str(e), self.is_debug)
            self.log.error("Panic attack!")

    def save_storage(self, player_name):
        file_name = self.storage_dir + player_name.lower().capitalize() + ".json"

        file_obj = File(file_name)
        data = {
            "last_online": self.last_online
        }

        if not file_obj.exists():
            self.log.debug(
                "{} file not found while saving data! Creating new...".format(file_name),
                self.is_debug
            )

        writer = FileWriter(file_obj)
        writer.write(self.gson.toJson(data))
        writer.close()

    def spawn_robot(self):
        world = get_world_by_name(self.default_world)
        store = world.getEntityStore().getStore()

        self.log.info("Booted! Waiting for any player...")
        player_ref = world.getPlayerRefs().iterator().next()
        self.log.debug("Choosing player {}...".format(player_ref.getUsername()), self.is_debug)

        transform = player_ref.getTransform()
        result = NPCPlugin.get().spawnNPC(
            store,
            "Horse",
            None,
            transform.getPosition(),
            Vector3f(0, 0, 0)
        )

        if result:
            self.log.info("Successfully spawned {}!".format(self.robot_name))
            self.robot_ref = result.first()

    def on_leave(self, event):
        player_name = event.getPlayerRef().getUsername()
        self.save_storage(player_name)
        try:
            # In-memory cleanup - would cause RAM go up quickly after a few joins and leaves.
            del self.player_x[player_name]
            del self.player_y[player_name]
            del self.player_z[player_name]
            del self.last_online[player_name]
            del self.player_rot_yaw[player_name]
            del self.player_rot_pitch[player_name]
            del self.player_world[player_name]
        except KeyError:
            pass

    def on(self):
        self.log.info("Booting...")

        try:
            os.mkdir(self.storage_dir)
        except:
            pass

        self.log.debug("Registering events...", self.is_debug)
        register_global(self.plugin, PlayerReadyEvent, self.on_join)
        register_global(self.plugin, PlayerDisconnectEvent, self.on_leave)

        # Run spawn_robot in main thread exposed by .jar as plugin.runOnMain
        self.plugin.runOnMain(self.spawn_robot)