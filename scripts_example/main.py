import unittest


class TestPython(unittest.TestCase):
    world = None
    logger = plugin.Log

    def test_exports_exists(self):
        self.assertIn("plugin", globals())
        self.assertIsNotNone(plugin)

        self.assertIn("init", globals())
        self.assertIsNotNone(init)

    def test_logging(self):
        from pygot.log import info, error, debug

        self.assertTrue(debug(self.logger, "Hello from Jython", True))
        self.assertFalse(debug(self.logger, "Hello from Jython", False))
        self.assertTrue(error(self.logger, "Hello from Jython"))
        self.assertTrue(info(self.logger, "Hello from Jython"))

    def test_world_lookup(self):
        from pygot.world import get_world_by_name

        self.world = get_world_by_name("default")
        self.assertIsNotNone(self.world)

    def test_event_registration(self):
        from com.hypixel.hytale.server.core.event.events.player import AddPlayerToWorldEvent

        from pygot.events import register_global
        from pygot.log import info

        self.assertTrue(register_global(
            plugin,
            AddPlayerToWorldEvent,
            lambda event: info(self.logger, event.toString())
        ))


if __name__ == "__main__":
    unittest.main(exit=False)