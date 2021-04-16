from typing import Dict

from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.utils.decorators import apply_defaults

from sai_airflow_plugins.operators.fabric_operator import FabricOperator


class FabricSensor(BaseSensorOperator, FabricOperator):
    """
    Executes a command on a remote host using the [Fabric](https://www.fabfile.org) library and returns True if and
    only if the exit code is 0. Like `FabricOperator` it uses a standard `SSHHook` for the connection configuration.

    The parameters for this sensor are the combined parameters of `FabricOperator` and `BaseSensorOperator`.
    """

    @apply_defaults
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def poke(self, context: Dict) -> bool:
        """
        Executes ``self.command`` over the configured SSH connection and checks its exit code.

        :param context: Context dict provided by airflow
        :return: True if the command's exit code was 0, else False.
        """
        result = self.execute_fabric_command()
        self.log.info(f"Fabric command exited with {result.exited}")

        return not result.exited
