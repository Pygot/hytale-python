# Java imports
from com.hypixel.hytale.server.core.universe.world.npc import INonPlayerCharacter
from com.hypixel.hytale.server.core.modules.entity.teleport import Teleport
from com.hypixel.hytale.server.core.command.system import CommandManager
from com.hypixel.hytale.server.core.event.events.player import (
    PlayerReadyEvent,
    PlayerDisconnectEvent,
    PlayerChatEvent
)
from com.hypixel.hytale.server.core.console import ConsoleSender
from  com.hypixel.hytale.server.npc.entities import NPCEntity
from com.hypixel.hytale.math.vector import Vector3f, Vector3d
from com.hypixel.hytale.component import RemoveReason
from com.hypixel.hytale.server.npc import NPCPlugin
from com.hypixel.hytale.server.core import Message
from java.io import File, FileReader, FileWriter
from java.lang import IllegalStateException
from java.util import Map, Objects
from com.google.gson import Gson

# Python imports
from pygot.entity import get_position, get_rotation
from pygot.world import get_world_by_name
from pygot.events import register_global
from datetime import datetime
from pygot.log import Log

import random, threading
import time, os


class Robot:
    def __init__(
            self,
            plugin,
            messages,
            enabled_cmds,
            robot_name="Robot",
            default_world="default",
            storage_dir="players_storage/",
            is_debug=False
    ):
        # Robot
        self.cmd_manager = CommandManager.get()
        self.log = Log(plugin.Log, is_debug)
        self.default_world = default_world
        self.enabled_cmds = enabled_cmds
        self.storage_dir = storage_dir
        self.robot_name = robot_name
        self.messages = messages
        self.robot_world = None
        self.robot_comp = None
        self.robot_ref = None
        self.plugin = plugin
        self.gson = Gson()
        # Players
        self.player_ref = None
        self.player_name = ""
        self.player_pos = {}
        self.player_rot = {}
        self.last_online = {}
        self.player_world = {}

    def on_chat(self, event):
        player = event.getSender()
        player_name = player.getUsername()
        message = event.getContent().lower()
        self.log.debug("{}: {}".format(player_name, message))

        if not message.startswith(self.robot_name.lower()):
            return

        message = message.split(" ")
        if len(message) < 2 or message[1] not in self.enabled_cmds:
            return

        if not self.player_pos.get(player_name):
            self.log.debug("{} not in player_pos variable".format(player_name))
            return

        cmd = message[1]

        if cmd == "tp":
            self.player_name = player_name
            self.plugin.runOnMain(self.teleport_robot)
        elif cmd == "hi":
            player.sendMessage(Message.raw(
                self.messages["prefix"] +
                self.messages["hi"].format(player_name)
            ))
        elif cmd == "die":
            self.player_name = player_name
            self.player_ref = player.getReference()
            self.plugin.runOnMain(self.die)

    def on_join(self, event):
        player = event.getPlayer()
        player_ref = player.getReference()
        player_name = player.getDisplayName()

        self.last_online[player_name] = datetime.now().isoformat()

        position = get_position(player_ref, player_ref.getStore())
        rotation = get_rotation(player_ref, player_ref.getStore())

        # Position
        if position:
            self.log.debug("Updating position of robot & {}".format(player_name))
            self.player_pos[player_name] = position
        else:
            self.log.debug(
                "Cannot update position for robot & {}! Position not found...".format(player_name)
            )

        # Rotation
        if rotation:
            self.log.debug("Updating rotation of robot & {}".format(player_name))
            self.player_rot[player_name] = rotation
        else:
            self.log.debug(
                "Cannot update rotation for robot & {}! Rotation not found...".format(player_name)
            )

        player.sendMessage(
            Message.raw(
                self.messages["prefix"] +
                self.messages["on_join"].format(player.getDisplayName())
            )
        )

        self.player_world[player_name] = get_world_by_name("default")

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
            self.log.error("Panic attack!")
            self.log.debug(str(e))

    def save_storage(self, player_name):
        file_name = self.storage_dir + player_name.lower().capitalize() + ".json"

        file_obj = File(file_name)
        data = {
            "last_online": self.last_online
        }

        if not file_obj.exists():
            self.log.debug(
                "{} file not found while saving data! Creating new...".format(file_name)
            )

        writer = FileWriter(file_obj)
        writer.write(self.gson.toJson(data))
        writer.close()

    def teleport_robot(self):
        if self.robot_comp and self.robot_ref.isValid():
            teleport = Teleport.createForPlayer(
                self.player_world[self.player_name],  # World
                self.player_pos[self.player_name],  # Position
                self.player_rot[self.player_name]  # Rotation
            )

            store = get_world_by_name(
                self.player_world[self.player_name].getName()
            ).getEntityStore().getStore()

            store.addComponent(self.robot_ref, Teleport.getComponentType(), teleport)  # Might not work at all
            self.log.debug(
                "Successfully teleported {} to player {}".format(
                    self.robot_name, self.player_name
                ))
        else:
            self.log.error("self.robot_ref is not valid!")

    def die(self):
        pos = self.player_pos[self.player_name]
        pos = Vector3d(pos.x, pos.y + 1000, pos.z)

        teleport = Teleport.createForPlayer(
            self.player_world[self.player_name],  # World
            pos,  # Position with +1000 y
            self.player_rot[self.player_name]  # Rotation
        )

        store = get_world_by_name(
            self.player_world[self.player_name].getName()
        ).getEntityStore().getStore()
        store.addComponent(self.player_ref, Teleport.getComponentType(), teleport)

        self.log.debug("Successfully tried {} die".format(self.player_name))

    def spawn_robot(self):
        self.robot_world = get_world_by_name(self.default_world)

        self.log.info("Booted! Waiting for any player...")
        while self.robot_world.getPlayerCount() < 1:  # Optional, it might block /plugin command
            time.sleep(1)

        def spawn():
            player_ref = self.robot_world.getPlayerRefs().iterator().next()
            self.log.debug("Choosing player {}...".format(player_ref.getUsername()))

            transform = player_ref.getTransform()
            result = NPCPlugin.get().spawnNPC(
                self.robot_world.getEntityStore().getStore(),
                "Robot_NPC",
                None,
                transform.getPosition(),
                Vector3f(0, 0, 0)
            )

            if result:
                self.log.info("Successfully spawned {}!".format(self.robot_name))
                self.robot_ref = result.first()
                self.robot_comp = self.robot_world.getEntityStore().getStore().getComponent(
                    self.robot_ref, Objects.requireNonNull(NPCEntity.getComponentType())
                )

        if not self.robot_comp:
            # Clean all NPCs to remove any Robot leftovers. Optional and not an optimal solution
            # Cannot be called in the main thread!
            self.log.debug("Cleaning all NPCs...")
            self.cmd_manager.handleCommand(ConsoleSender.INSTANCE, "npc clean --world={} --confirm".format(self.default_world))
            # Run spawn() in the main thread
            self.plugin.runOnMain(spawn)

    def on_leave(self, event):
        player_name = event.getPlayerRef().getUsername()
        self.save_storage(player_name)
        try:
            # In-memory cleanup - would cause RAM go up quickly after a few joins and leaves.
            del self.player_pos[player_name]
            del self.player_rot[player_name]
            del self.last_online[player_name]
            del self.player_world[player_name]
        except KeyError:
            pass

    def on(self):
        self.log.info("Booting...")

        try:
            os.mkdir(self.storage_dir)
        except:
            pass

        self.log.debug("Registering events...")
        register_global(self.plugin, PlayerReadyEvent, self.on_join)
        register_global(self.plugin, PlayerDisconnectEvent, self.on_leave)
        register_global(self.plugin, PlayerChatEvent, self.on_chat)

        robot_thread = threading.Thread(target=self.spawn_robot)
        robot_thread.setDaemon(True)
        robot_thread.start()