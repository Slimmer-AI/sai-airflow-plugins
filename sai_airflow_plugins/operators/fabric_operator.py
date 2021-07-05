from typing import Dict, List, Any, Optional

from airflow.exceptions import AirflowException
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from fabric import Result
from invoke import Responder, StreamWatcher

from sai_airflow_plugins.hooks.fabric_hook import FabricHook


class FabricOperator(BaseOperator):
    """
    Operator to execute commands on a remote host using the [Fabric](https://www.fabfile.org) library.
    It uses `FabricHook` for the connection configuration, which is derived from the standard `SSHHook`.

    The advantage of this operator over the standard `SSHOperator` is that you can add watchers that respond to
    specific command output. A number of predefined watchers are included in this operator. Note, however, that
    some of these require the FabricHook to be configured with a password and not a private key.

    :param fabric_hook: predefined fabric_hook to use for remote execution. Either `fabric_hook` or `ssh_conn_id` needs
                        to be provided.
    :param ssh_conn_id: connection id from airflow Connections. `ssh_conn_id` will be ignored if `fabric_hook` is
                        provided. (templated)
    :param remote_host: remote host to connect. (templated) Nullable. If provided, it will replace the `remote_host`
                        which was defined in `fabric_hook` or predefined in the connection of `ssh_conn_id`.
    :param command: command to execute on remote host. (templated)
    :param use_sudo: uses Fabric's sudo function instead of run. Because this function automatically adds a responder
                     for the password prompt, parameter `add_sudo_password_responder` will be ignored. It uses the
                     SSH connection's password as reply.
    :param sudo_user: If `use_sudo` is `True`, run the command as this user. If not supplied it will run as root.
                      This parameter is ignored if `use_sudo` is `False`.
    :param watchers: Watchers for responding to specific command output. This is a list of dicts specifying a class
                     of type ``StreamWatcher`` and its arguments. For each dict the corresponding object is created
                     and added to Fabric's run function. It's done this way because arguments to an operator are
                     pickled and StreamWatcher objects are derived from thread.local which can't be pickled.
                     Example:
                     >>> {"watchers": [{"class": Responder, "pattern": r"Continue\\?", "response": "yes\\n"}]}
                     See also: http://docs.pyinvoke.org/en/latest/concepts/watchers.html
    :param add_sudo_password_responder: adds a responder for the sudo password prompt. It replies with the password of
                                        the SSH connection. Set this to True if your command contains one or more sudo
                                        statements. If you use `use_sudo` instead, then don't use this parameter.
    :param add_generic_password_responder: adds a responder for a generic password prompt. It replies with the password
                                           of the SSH connection. This is useful if you execute other ssh commands on
                                           the remote host, for example scp and rsync.
    :param add_unknown_host_key_responder: adds a responder for a host authenticity check with an unknown key.
                                           It replies ``yes`` to continue connecting. This is useful if you execute
                                           other ssh commands on the remote host, for example scp and rsync.
    :param connect_timeout: Connection timeout, in seconds. The default is 10.
    :param environment: a dict of shell environment variables. Note that the server will reject them silently if
                        `AcceptEnv` is not set in SSH config. In such cases setting `inline_ssh_env` to True may help.
                        (templated)
    :param inline_ssh_env: whether to send environment variables "inline" as prefixes in front of command strings
                           (export VARNAME=value && mycommand here), instead of trying to submit them through the SSH
                           protocol itself (which is the default behavior). This is necessary if the remote server
                           has a restricted AcceptEnv setting (which is the common default).
    :param xcom_push_key: push stdout to an XCom with this key. If None (default), or stdout is empty, then no XCom
                          will be pushed.
    :param strip_stdout: strip leading and trailing whitespace from stdout. Useful, for example, when pushing stdout
                         to an XCom and you don't want a trailing newline in it.
    :param get_pty: request a pseudo-terminal from the server, instead of connecting directly to the stdout/stderr
                    streams. This may be necessary when running programs that require a terminal. Note that stderr
                    output will be included in stdout, and thus added to an XCom when using `xcom_push_key`.
    """

    template_fields = ("ssh_conn_id", "command", "remote_host", "environment")
    template_ext = (".sh",)
    ui_color = "#ebfaff"

    @apply_defaults
    def __init__(self,
                 fabric_hook: Optional[FabricHook] = None,
                 ssh_conn_id: Optional[str] = None,
                 remote_host: Optional[str] = None,
                 command: str = None,
                 use_sudo: Optional[bool] = False,
                 sudo_user: Optional[str] = None,
                 watchers: Optional[List[Dict[str, Any]]] = None,
                 add_sudo_password_responder: Optional[bool] = False,
                 add_generic_password_responder: Optional[bool] = False,
                 add_unknown_host_key_responder: Optional[bool] = False,
                 connect_timeout: Optional[int] = 10,
                 environment: Optional[Dict[str, Any]] = None,
                 inline_ssh_env: Optional[bool] = False,
                 xcom_push_key: Optional[str] = None,
                 strip_stdout: Optional[bool] = False,
                 get_pty: Optional[bool] = False,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.fabric_hook = fabric_hook
        self.ssh_conn_id = ssh_conn_id
        self.remote_host = remote_host
        self.command = command
        self.use_sudo = use_sudo
        self.sudo_user = sudo_user
        self.watchers = watchers or []
        self.add_sudo_password_responder = False if self.use_sudo else add_sudo_password_responder
        self.add_generic_password_responder = add_generic_password_responder
        self.add_unknown_host_key_responder = add_unknown_host_key_responder
        self.connect_timeout = connect_timeout
        self.environment = environment or {}
        self.inline_ssh_env = inline_ssh_env
        self.xcom_push_key = xcom_push_key
        self.strip_stdout = strip_stdout
        self.get_pty = get_pty

    def execute(self, context: Dict):
        """
        Executes ``self.command`` over the configured SSH connection.

        :param context: Context dict provided by airflow
        :return: True or the connection's stdout if ``self.do_xcom_push`` is True.
                 On an error, raises AirflowException.
        """
        result = self.execute_fabric_command()

        if result.exited == 0:
            # Push the output to an XCom if requested
            if self.xcom_push_key and result.stdout:
                task_inst = context["task_instance"]
                task_inst.xcom_push(self.xcom_push_key, result.stdout)

            return True
        else:
            raise AirflowException(f"Command exited with return code {result.exited}. See log output for details.")

    def execute_fabric_command(self) -> Result:
        """
        Executes ``self.command`` over the configured SSH connection.

        :return: The `Result` object from Fabric's `run` method
        """
        try:
            if self.fabric_hook and isinstance(self.fabric_hook, FabricHook):
                if self.ssh_conn_id:
                    self.log.info("ssh_conn_id is ignored when fabric_hook is provided.")

                if self.remote_host is not None:
                    self.log.info("remote_host is provided explicitly. It will replace the remote_host which was "
                                  "defined in fabric_hook.")
                    self.fabric_hook.remote_host = self.remote_host

            elif self.ssh_conn_id:
                self.log.info("fabric_hook is not provided or invalid. Trying ssh_conn_id to create FabricHook.")
                if self.remote_host is None:
                    self.fabric_hook = FabricHook(ssh_conn_id=self.ssh_conn_id,
                                                  timeout=self.connect_timeout,
                                                  inline_ssh_env=self.inline_ssh_env)
                else:
                    # Prevent empty `SSHHook.remote_host` field which would otherwise raise an exception
                    self.log.info("remote_host is provided explicitly. It will replace the remote_host which was "
                                  "predefined in the connection specified by ssh_conn_id.")
                    self.fabric_hook = FabricHook(ssh_conn_id=self.ssh_conn_id,
                                                  remote_host=self.remote_host,
                                                  timeout=self.connect_timeout,
                                                  inline_ssh_env=self.inline_ssh_env)

            else:
                raise AirflowException("Cannot operate without fabric_hook or ssh_conn_id.")

            if not self.command:
                raise AirflowException("SSH command not specified. Aborting.")

            conn = self.fabric_hook.get_fabric_conn()

            # Create watcher objects, using the provided dictionary to instantiate the class and supply its kwargs
            watchers = []
            for watcher_dict in self.watchers:
                try:
                    watcher_class = watcher_dict.pop("class")
                except KeyError:
                    self.log.info(f"Watcher class missing. Defaulting to {Responder}.")
                    watcher_class = Responder

                if not issubclass(watcher_class, StreamWatcher):
                    raise AirflowException(
                        f"The class attribute of a watcher dict must contain a subclass of {StreamWatcher}."
                    )

                watcher = watcher_class(**watcher_dict)
                watchers.append(watcher)

            # Add predefined watchers
            if self.add_sudo_password_responder:
                watchers.append(self.fabric_hook.get_sudo_pass_responder())

            if self.add_generic_password_responder:
                watchers.append(self.fabric_hook.get_generic_pass_responder())

            if self.add_unknown_host_key_responder:
                watchers.append(self.fabric_hook.get_unknown_host_key_responder())

            if self.use_sudo:
                if self.sudo_user:
                    self.log.info(f"Running sudo command as '{self.sudo_user}': {self.command}")
                else:
                    self.log.info(f"Running sudo command: {self.command}")
            else:
                self.log.info(f"Running command: {self.command}")

            if self.environment:
                formatted_env_msg = "\n".join(f"{k}={v}" for k, v in self.environment.items())
                self.log.info(f"With environment variables:\n{formatted_env_msg}")

            run_kwargs = dict(
                command=self.command,
                pty=self.get_pty,
                env=self.environment,
                watchers=watchers,
                warn=True  # don't directly raise an UnexpectedExit when the exit code is non-zero
            )

            if self.use_sudo:
                run_kwargs["password"] = self.fabric_hook.password
                if self.sudo_user:
                    run_kwargs["user"] = self.sudo_user
                res = conn.sudo(**run_kwargs)
            else:
                res = conn.run(**run_kwargs)

            # Strip stdout if requested
            if res.stdout and self.strip_stdout:
                res.stdout = res.stdout.strip()

            return res

        except Exception as e:
            raise AirflowException(f"Fabric operator error: {e}")
