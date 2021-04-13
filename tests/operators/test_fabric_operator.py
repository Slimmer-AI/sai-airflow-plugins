import unittest
from unittest.mock import Mock

from airflow.exceptions import AirflowException
from fabric import Connection
from faker import Faker
from invoke import Responder

from sai_airflow_plugins.hooks.fabric_hook import FabricHook
from sai_airflow_plugins.operators.fabric_operator import FabricOperator

TEST_TASK_ID = "test_fabric_operator"

faker = Faker()


class MockedFabricHook(FabricHook):
    exit_code = 0
    stdout = faker.text()

    def get_fabric_conn(self) -> Connection:
        conn = super().get_fabric_conn()
        mock_result = Mock()
        mock_result.exited = self.exit_code
        mock_result.stdout = self.stdout
        mock_result.conn = conn
        conn.run = Mock(return_value=mock_result)
        return conn


class FabricOperatorTest(unittest.TestCase):

    def setUp(self):
        self.hook = MockedFabricHook(
            remote_host=faker.hostname(),
            username=faker.user_name(),
            password=faker.password()
        )

    def test_ssh_conn_id_or_fabric_hook_required(self):
        """
        Test that either ssh_conn_id or fabric_hook is required for execution
        """
        op = FabricOperator(task_id=TEST_TASK_ID, command="ls")
        with self.assertRaises(AirflowException) as assertion:
            op.execute(context={})
            self.assertIn("ssh_conn_id", str(assertion.exception))
            self.assertIn("fabric_hook", str(assertion.exception))

    def test_command_required(self):
        """
        Test that command is required for execution
        """
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook)

        with self.assertRaises(AirflowException):
            op.execute(context={})

    def test_fabric_operator_execute_success(self):
        """
        Test that execution with a zero exit code succeeds and called connection.run with the correct parameters
        """
        command = faker.text()
        env = faker.pydict()
        pty = faker.pybool()
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command=command, environment=env, get_pty=pty)

        self.assertTrue(op.execute(context={}))

        res = op.execute_fabric_command()
        res.conn.run.assert_called_with(command=command, pty=pty, env=env, watchers=[], warn=True)

    def test_fabric_operator_execute_non_zero_exit(self):
        """
        Test that execution with a non-zero exit code fails and the exit code is logged
        """
        self.hook.exit_code = faker.pyint(min_value=1)
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls")

        with self.assertRaises(AirflowException) as assertion:
            op.execute(context={})
            self.assertIn(self.hook.exit_code, str(assertion.exception))

    def test_remote_host_override(self):
        """
        Test that remote_host can be overridden so it uses that one instead of hook.remote_host
        """
        remote_host = faker.hostname()
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls", remote_host=remote_host)
        res = op.execute_fabric_command()

        self.assertEqual(res.conn.host, remote_host)

    def test_pty_true_with_sudo(self):
        """
        Test that get_pty is always True if command starts with "sudo" or the sudo password responder is added
        """
        op1 = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="sudo ls")
        self.assertTrue(op1.get_pty)

        op2 = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls",
                             add_sudo_password_responder=True)
        self.assertTrue(op2.get_pty)

    def test_watcher(self):
        """
        Test that a watcher dict is converted correctly into the specified Watcher object
        """
        watcher_dict = {
            "class": Responder,
            "pattern": r"Ping\?:",
            "response": "Pong\n"
        }
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls", watchers=[watcher_dict])
        res = op.execute_fabric_command()
        watchers = res.conn.run.call_args[1]["watchers"]

        self.assertEqual(len(watchers), 1)
        self.assertIsInstance(watchers[0], Responder)
        self.assertEqual(watchers[0].pattern, watcher_dict["pattern"])
        self.assertEqual(watchers[0].response, watcher_dict["response"])

    def test_bad_watchers(self):
        """
        Test that a wrong watcher class or a watcher without the required parameters raises an exception
        """
        op1 = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls", watchers=[{"class": object}])
        with self.assertRaises(AirflowException):
            res = op1.execute_fabric_command()

        op2 = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls",
                             watchers=[{"class": Responder}])
        with self.assertRaises(AirflowException):
            res = op2.execute_fabric_command()

    def test_predefined_watchers(self):
        """
        Test that predefined watchers in `FabricHook` are correctly added when the add flags are True
        """
        self.hook.get_sudo_pass_responder = Mock()
        self.hook.get_generic_pass_responder = Mock()
        self.hook.get_unknown_host_key_responder = Mock()

        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls",
                            add_sudo_password_responder=True,
                            add_generic_password_responder=True,
                            add_unknown_host_key_responder=True)
        res = op.execute_fabric_command()
        watchers = res.conn.run.call_args[1]["watchers"]

        self.assertEqual(len(watchers), 3)
        self.hook.get_sudo_pass_responder.assert_called()
        self.hook.get_generic_pass_responder.assert_called()
        self.hook.get_unknown_host_key_responder.assert_called()

    def test_xcom_push(self):
        """
        Test that an XCom is pushed with the specified name as key and the stdout as value if `xcom_push_key` is set
        """
        task_inst = Mock()
        op = FabricOperator(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls", xcom_push_key="test_xcom")
        op.execute(context={"task_instance": task_inst})

        task_inst.xcom_push.assert_called_with("test_xcom", self.hook.stdout)
