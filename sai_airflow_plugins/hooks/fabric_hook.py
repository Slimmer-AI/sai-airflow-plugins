from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.exceptions import AirflowException
from fabric import Connection
from invoke import FailingResponder


class FabricHook(SSHHook):
    """
    This hook allows you to connect to an SSH remote host and run commands on it using the
    [Fabric](https://www.fabfile.org) library. It inherits from `SSHHook` and uses its input arguments for setting
    up the connection.

    :param ssh_conn_id: connection id from airflow Connections
    :param inline_ssh_env: whether to send environment variables "inline" as prefixes in front of command strings
                           (export VARNAME=value && mycommand here), instead of trying to submit them through the SSH
                           protocol itself (which is the default behavior). This is necessary if the remote server
                           has a restricted AcceptEnv setting (which is the common default).
    """

    def __init__(self,
                 ssh_conn_id: str = None,
                 inline_ssh_env: bool = False,
                 *args,
                 **kwargs):
        kwargs["ssh_conn_id"] = ssh_conn_id
        super().__init__(*args, **kwargs)
        self.inline_ssh_env = inline_ssh_env

    def get_fabric_conn(self) -> Connection:
        """
        Creates a Fabric `Connection` object using the settings in this hook.

        :return: `Connection` object
        """
        self.log.info(
            f"Setting up fabric connection for conn_id: {self.ssh_conn_id} to remote host: {self.remote_host}"
        )

        connect_kwargs = {
            "compress": self.compress
        }

        if self.password:
            password = self.password.strip()
            connect_kwargs["password"] = password

        if self.pkey:
            connect_kwargs["pkey"] = self.pkey

        if self.key_file:
            connect_kwargs["key_filename"] = self.key_file

        if self.host_proxy:
            connect_kwargs["sock"] = self.host_proxy

        return Connection(
            host=self.remote_host,
            user=self.username,
            port=self.port,
            connect_timeout=self.timeout,
            connect_kwargs=connect_kwargs,
            inline_ssh_env=self.inline_ssh_env
        )

    def get_sudo_pass_responder(self) -> FailingResponder:
        """
        Creates a responder for the sudo password prompt. It replies with the password of the SSH connection.
        Note: only use this if the SSH connection is configured with a password and not a key.

        :return: `FailingResponder` object; raises `AirflowException` if no password was configured in the connection
        """
        if not self.password:
            raise AirflowException("`add_sudo_password_responder` requires an SSH connection with a password.")

        return FailingResponder(
            pattern=r"\[sudo\] password for ",
            response=f"{self.password}\n",
            sentinel="Sorry, try again.\n"
        )

    def get_generic_pass_responder(self) -> FailingResponder:
        """
        Creates a responder for a generic password prompt. It replies with the password of the SSH connection. This is
        useful if you execute other ssh commands on the remote host, for example scp and rsync.
        Note: only use this if the SSH connection is configured with a password and not a key.

        :return: `FailingResponder` object; raises `AirflowException` if no password was configured in the connection
        """
        if not self.password:
            raise AirflowException("`add_generic_password_responder` requires an SSH connection with a password.")

        return FailingResponder(
            pattern=r"password: ",
            response=f"{self.password}\n",
            sentinel="Permission denied"
        )

    @staticmethod
    def get_unknown_host_key_responder() -> FailingResponder:
        """
        Creates a responder for a host authenticity check with an unknown key. It replies ``yes`` to continue
        connecting. This is useful if you execute other ssh commands on the remote host, for example scp and rsync.

        :return: `FailingResponder` object
        """
        return FailingResponder(
            pattern=r"Are you sure you want to continue connecting \(yes/no\)\? ",
            response="yes\n",
            sentinel="Host key verification failed.\n"
        )
