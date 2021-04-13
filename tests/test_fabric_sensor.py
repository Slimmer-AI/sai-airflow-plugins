import unittest

from faker import Faker

from sai_airflow_plugins.sensors.fabric_sensor import FabricSensor
from tests.mocked_fabric_hook import MockedFabricHook

TEST_TASK_ID = "test_fabric_sensor"

faker = Faker()


class FabricSensorTest(unittest.TestCase):

    def setUp(self):
        self.hook = MockedFabricHook(
            remote_host=faker.hostname(),
            username=faker.user_name(),
            password=faker.password()
        )

    def test_fabric_sensor_with_zero_exit_code(self):
        """
        Test that poke returns True in case of a zero exit code
        """
        op = FabricSensor(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls")
        self.assertTrue(op.poke(context={}))

    def test_fabric_sensor_with_non_zero_exit_code(self):
        """
        Test that poke returns True in case of a zero exit code
        """
        self.hook.exit_code = faker.pyint(min_value=1)
        op = FabricSensor(task_id=TEST_TASK_ID, fabric_hook=self.hook, command="ls")
        self.assertFalse(op.poke(context={}))
