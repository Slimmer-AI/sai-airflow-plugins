import getpass
import unittest

from airflow.exceptions import AirflowException
from faker import Faker
from invoke import FailingResponder
from paramiko.config import SSH_PORT

from sai_airflow_plugins.hooks.fabric_hook import FabricHook

faker = Faker()


class GetFabricConnectionTest(unittest.TestCase):

    def setUp(self):
        self.kwargs = dict(
            remote_host=faker.hostname(),
            username=faker.user_name(),
            password=faker.password(),
            key_file=faker.file_path(),
            port=faker.port_number(),
            timeout=faker.pyint(),
            inline_ssh_env=faker.pybool()
        )

        # These options can normally only be set when using an ssh_conn_id from db, not directly via the constructor
        self.pkey = faker.pystr()
        self.compress = faker.pybool()
        self.host_proxy = faker.hostname()

    def test_get_fabric_conn_all_opts(self):
        """
        The Connection object must have all options that were specified in FabricHook
        """
        hook = FabricHook(**self.kwargs)
        hook.pkey = self.pkey
        hook.compress = self.compress
        hook.host_proxy = self.host_proxy
        conn = hook.get_fabric_conn()

        self.assertEqual(conn.host, self.kwargs["remote_host"])
        self.assertEqual(conn.user, self.kwargs["username"])
        self.assertEqual(conn.port, self.kwargs["port"])
        self.assertEqual(conn.connect_timeout, self.kwargs["timeout"])
        self.assertEqual(conn.connect_kwargs["password"], self.kwargs["password"])
        self.assertEqual(conn.connect_kwargs["key_filename"], self.kwargs["key_file"])
        self.assertEqual(conn.connect_kwargs["pkey"], self.pkey)
        self.assertEqual(conn.connect_kwargs["compress"], self.compress)
        self.assertEqual(conn.connect_kwargs["sock"], self.host_proxy)
        self.assertEqual(conn.inline_ssh_env, self.kwargs["inline_ssh_env"])

    def test_get_fabric_conn_default_opts(self):
        """
        The Connection object must have default options that were specified in FabricHook or empty ones in case of
        optional connect_kwargs
        """
        hook = FabricHook(remote_host=self.kwargs["remote_host"])
        conn = hook.get_fabric_conn()

        self.assertEqual(conn.user, getpass.getuser())
        self.assertEqual(conn.port, SSH_PORT)
        self.assertEqual(conn.connect_timeout, 10)
        self.assertTrue(conn.connect_kwargs["compress"])
        self.assertNotIn("password", conn.connect_kwargs)
        self.assertNotIn("key_filename", conn.connect_kwargs)
        self.assertNotIn("pkey", conn.connect_kwargs)
        self.assertNotIn("sock", conn.connect_kwargs)
        self.assertFalse(conn.inline_ssh_env)


class RespondersTest(unittest.TestCase):

    def setUp(self):
        self.remote_host = faker.hostname()
        self.username = faker.user_name()
        self.password = faker.password()

    def test_sudo_pass_responder_requires_password(self):
        """
        Test that the sudo password responder requires a password in the hook object
        """
        hook = FabricHook(remote_host=self.remote_host)
        with self.assertRaises(AirflowException) as assertion:
            hook.get_sudo_pass_responder()
            self.assertIn("password", str(assertion.exception))

    def test_generic_pass_responder_requires_password(self):
        """
        Test that the generic password responder requires a password in the hook object
        """
        hook = FabricHook(remote_host=self.remote_host)
        with self.assertRaises(AirflowException) as assertion:
            hook.get_generic_pass_responder()
            self.assertIn("password", str(assertion.exception))

    def test_sudo_pass_responder_responds_with_password(self):
        """
        Test that the sudo password responder is a FailingResponder and responds with the password in the hook object
        """
        hook = FabricHook(remote_host=self.remote_host, username=self.username, password=self.password)
        responder = hook.get_sudo_pass_responder()
        self.assertIsInstance(responder, FailingResponder)
        self.assertEqual(responder.response, self.password + "\n")

    def test_generic_pass_responder_responds_with_password(self):
        """
        Test that the generic password responder is a FailingResponder responds with the password in the hook object
        """
        hook = FabricHook(remote_host=self.remote_host, username=self.username, password=self.password)
        responder = hook.get_generic_pass_responder()
        self.assertIsInstance(responder, FailingResponder)
        self.assertEqual(responder.response, self.password + "\n")
