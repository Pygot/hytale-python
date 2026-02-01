from com.hypixel.hytale.server.core.asset.type.model.config import ModelAsset, Model
from com.hypixel.hytale.server.core.universe.world.storage import EntityStore
from com.hypixel.hytale.server.core.modules.entity.tracker import NetworkId
from com.hypixel.hytale.server.core.modules.interaction import Interactions
from com.hypixel.hytale.server.core.modules.entity.component import (
    TransformComponent,
    PersistentModel,
    BoundingBox,
    ModelComponent
)
from com.hypixel.hytale.server.core.event.events.player import (
    PlayerReadyEvent,
    PlayerDisconnectEvent
)
from com.hypixel.hytale.server.core.entity.entities import Player
from com.hypixel.hytale.component import AddReason, RemoveReason
from com.hypixel.hytale.server.core.entity import UUIDComponent
from com.hypixel.hytale.math.vector import Vector3d, Vector3f
from com.hypixel.hytale.server.npc.entities import NPCEntity
from com.hypixel.hytale.server.core import Message
from java.io import File, FileReader, FileWriter
from com.google.gson import Gson
from java.util import Map, UUID

from pygot.entity import get_position, get_rotation
from pygot.world import get_world_by_name
from pygot.events import register_global
from pygot.log import error, info, debug

from datetime import datetime

import threading, time, os


class Robot:
    def __init__(self, plugin, messages, robot_name="Robot", default_world="default", storage_dir="players_storage/", is_debug=False):
        # Robot
        self.default_world = default_world
        self.storage_dir = storage_dir
        self.robot_name = robot_name
        self.is_debug = is_debug
        self.logger = plugin.Log
        self.messages = messages
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
            debug(self.logger, "Updating position of robot & {}".format(player_name), self.is_debug)
            x, y, z = position.x, position.y, position.z
            self.player_x[player_name], self.x = x, x
            self.player_y[player_name], self.y = y, y
            self.player_z[player_name], self.z = z, z
        else:
            debug(
                self.logger,
                "Cannot update position for robot & {}! Position not found...".format(player_name), self.is_debug
            )

        # Rotation
        if rotation:
            debug(self.logger, "Updating rotation of robot & {}".format(player_name), self.is_debug)
            x, y = rotation.x, rotation.y
            self.player_rot_yaw[player_name], self.rot_yaw = x, x
            self.player_rot_pitch[player_name], self.rot_y = y, y
        else:
            debug(
                self.logger,
                "Cannot update rotation for robot & {}! Rotation not found...".format(player_name), self.is_debug
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
            error(self.logger, "No {} found! Creating...".format(file_name))
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
            debug(self.logger, str(e), self.is_debug)
            error(self.logger, "Panic attack!")

    def save_storage(self, player_name):
        file_name = self.storage_dir + player_name.lower().capitalize() + ".json"

        file_obj = File(file_name)
        data = {
            "last_online": self.last_online
        }

        if not file_obj.exists():
            debug(self.logger, "{} file not found while saving data! Creating new...".format(file_name), self.is_debug)

        writer = FileWriter(file_obj)
        writer.write(self.gson.toJson(data))
        writer.close()

    def spawn_robot(self):
        def readd_robot_and_save():
            world = get_world_by_name(self.default_world)
            store = world.getEntityStore().getStore()

            holder = EntityStore.REGISTRY.newHolder()

            model_asset = ModelAsset.getAssetMap().getAsset("Minecart")
            model = Model.createScaledModel(model_asset, 10.0)

            position = Vector3d(-596, 122.0, -152.0)
            rotation = Vector3f(0.0, 0.0)

            holder.addComponent(TransformComponent.getComponentType(), TransformComponent(position, rotation))
            holder.addComponent(PersistentModel.getComponentType(), PersistentModel(model.toReference()))
            holder.addComponent(ModelComponent.getComponentType(), ModelComponent(model))
            holder.addComponent(BoundingBox.getComponentType(), BoundingBox(model.getBoundingBox()))
            holder.addComponent(NetworkId.getComponentType(), NetworkId(store.getExternalData().takeNextNetworkId()))
            holder.addComponent(Interactions.getComponentType(), Interactions())
            holder.ensureComponent(UUIDComponent.getComponentType())

            store.addEntity(holder, AddReason.SPAWN)

        self.plugin.runOnMain(readd_robot_and_save)
        info(self.logger, "Booted!")

    def on_leave(self, event):
        player_name = event.getPlayerRef().getUsername()
        self.save_storage(player_name)
        # In-memory cleanup - would cause RAM go up quickly after a few joins and leaves.
        del self.player_x[player_name]
        del self.player_y[player_name]
        del self.player_z[player_name]
        del self.last_online[player_name]
        del self.player_rot_yaw[player_name]
        del self.player_rot_pitch[player_name]
        del self.player_world[player_name]

    def on(self):
        info(self.logger, "Booting...")

        try:
            os.mkdir(self.storage_dir)
        except:
            pass

        debug(self.logger, "Registering events...", self.is_debug)
        register_global(self.plugin, PlayerReadyEvent, self.on_join)
        register_global(self.plugin, PlayerDisconnectEvent, self.on_leave)

        # Run everything else outside the main thread to prevent blockage
        robot_thread = threading.Thread(target=self.spawn_robot)
        robot_thread.setDaemon(True)
        robot_thread.start()
