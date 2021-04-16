Basic usage
===========

.. contents:: Contents
    :depth: 2
    :local:


Fabric operators
----------------

Use :class:`~sai_airflow_plugins.operators.fabric_operator.FabricOperator` to execute a command over SSH using the
`Fabric <https://www.fabfile.org/>`_ library, with e.g. a sudo password responder:

.. code-block:: python

    op = FabricOperator(
        task_id="example_fabric_task",
        dag_id="my_dag",
        ssh_conn_id="ssh_default",
        remote_host="my.remote.host",
        command="sudo ls -al ",
        add_sudo_password_responder=True
    )

You can use a :class:`~sai_airflow_plugins.hooks.fabric_hook.FabricHook` instead of an ``ssh_conn_id``:

.. code-block:: python

    hook = FabricHook(
        remote_host="my.remote.host",
        username="my.user",
        password="mypass"
    )

    op = FabricOperator(
        task_id="example_fabric_task",
        dag_id="my_dag",
        fabric_hook=hook,
        command="my_shell_script.sh"
    )

Use a :class:`~sai_airflow_plugins.sensors.fabric_sensor.FabricSensor` to wait until a command results in
exit code ``0``:

.. code-block:: python

    op = FabricSensor(
        task_id="example_fabric_task",
        dag_id="my_dag",
        poke_interval=60,
        timeout=3600,
        mode="reschedule",
        ssh_conn_id="ssh_default",
        command="test -f {{ params.my_file" }} ",
        params={"my_file": "very_important_data.bin"}
    )


Mattermost operator
-------------------

Use :class:`~sai_airflow_plugins.operators.mattermost_webhook_operator.MattermostWebhookOperator` for a task that sends
a message to an `incoming Mattermost webhook <https://docs.mattermost.com/developer/webhooks-incoming.html>`_.

The HTTP ``Connection`` that you specify with ``http_conn_id`` should contain a ``webhook_token`` in its ``extras``
field. Alternatively you can supply it in the operator:

.. code-block:: python

    op = MattermostWebhookOperator(
        task_id="example_mattermost_task",
        dag_id="my_dag",
        http_conn_id="http_mattermost",
        webhook_token="[webhook token]",
        message="Execution date: {{ ds }}"
    )

You can also send a message without using a pre-defined Airflow ``Connection`` object, by specifying the complete
webhook URL in the operator's ``webhook_token``:

.. code-block:: python

    op = MattermostWebhookOperator(
        task_id="example_mattermost_task",
        dag_id="my_dag",
        webhook_token="https://my.mattermost.host/[webhook token]",
        message="Something went wrong",
        icon_emoji=":boom:"
    )


Conditional operators
---------------------

Use :class:`~sai_airflow_plugins.operators.conditional_skip_mixin.ConditionalSkipMixin` to add a Python condition to
an operator. The task will be skipped if the condition evaluates to False. Example:

.. code-block:: python

    class MyConditionalOperator(ConditionalSkipMixin, MyOperator):
        template_fields = MyOperator.template_fields + ConditionalSkipMixin.template_fields
        ui_color = "#ff0000"

    op = ConditionalTestOperator(
        task_id="example_conditional_task",
        dag_id="my_dag",
        condition_callable=lambda my_arg, **kwargs: kwargs["task_instance"].try_number == my_param
        condition_kwargs={"my_arg": 2},
        condition_provide_context=True
    )

The mixin also works with sensors:

.. code-block:: python

    op = ConditionalBashSensor(
        task_id="example_conditional_task",
        dag_id="my_dag",
        poke_interval=60,
        timeout=3600,
        bash_command="test -f very_important_data.bin ",
        condition_callable=lambda my_arg, **kwargs: kwargs["task_instance"].try_number == my_param
        condition_args=[2],
        condition_provide_context=True
    )

You can find several predefined conditional operators in modules
:mod:`~sai_airflow_plugins.operators.conditional_operators` and :mod:`~sai_airflow_plugins.sensors.conditional_sensors`.
