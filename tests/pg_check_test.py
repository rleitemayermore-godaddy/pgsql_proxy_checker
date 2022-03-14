from .context import pg_check
import unittest
import os


class BasicTests(unittest.TestCase):
    """ Basic test case """

    def setUp(self):
        self.pgcheck = pg_check.PgCheck()
        self.pgcheck.read_config()

    def tearDown(self):
        if os.path.isfile("/tmp/node_disabled"):
            os.remove("/tmp/node_disabled")
        if self.pgcheck.connection is not None:
            self.pgcheck.connection.close()

    def test_disabling_node(self):
        assert(self.pgcheck.disabled is False)

    def test_disable_node(self):
        """ This test explicitly sets the disable status for testing purposes"""
        open("/tmp/node_disabled", 'a').close() if not os.path.isfile("/tmp/node_disabled") else False
        self.pgcheck.is_enabled()
        assert self.pgcheck.disabled

    def test_get_port(self):
        assert(self.pgcheck.port == 5432)

    def test_get_host(self):
        assert(self.pgcheck.hostname == "web1.moreira.dom")

    def test_get_user(self):
        assert(self.pgcheck.user == "numberninja")

    def test_connect(self):
        self.pgcheck.connect()
        self.pgcheck.check_recovery_mode()
        print(self.pgcheck.is_master)
        print(self.pgcheck.is_slave)
        self.pgcheck.reply()
        assert(self.pgcheck.connection is not None)


if __name__ == '__main__':
    unittest.main()

