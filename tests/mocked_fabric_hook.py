from unittest.mock import Mock

from fabric import Connection

from sai_airflow_plugins.hooks.fabric_hook import FabricHook


class MockedFabricHook(FabricHook):
    exit_code = 0
    stdout = "Command completed successfully\n"

    def get_fabric_conn(self) -> Connection:
        """
        Mocks Fabric's connection.run and connection.sudo functions, returning a result with an exit code, stdout and
        the conn object
        """
        conn = super().get_fabric_conn()
        mock_result = Mock()
        mock_result.exited = self.exit_code
        mock_result.stdout = self.stdout
        mock_result.conn = conn
        conn.run = Mock(return_value=mock_result)
        conn.sudo = Mock(return_value=mock_result)
        return conn
