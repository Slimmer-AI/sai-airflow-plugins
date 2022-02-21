Changelog
=========

0.1.0
-----

*(2021-04-16)*

- Added SSH connectivity with the Fabric library
    - :class:`~sai_airflow_plugins.hooks.fabric_hook.FabricHook`,
      :class:`~sai_airflow_plugins.operators.fabric_operator.FabricOperator` and
      :class:`~sai_airflow_plugins.sensors.fabric_sensor.FabricSensor`
- Added Mattermost integration
    - :class:`~sai_airflow_plugins.hooks.mattermost_webhook_hook.MattermostWebhookHook` and
      :class:`~sai_airflow_plugins.operators.mattermost_webhook_operator.MattermostWebhookOperator`
- Added conditional operator mixin that skips when the condition is False
    - :class:`~sai_airflow_plugins.operators.conditional_skip_mixin.ConditionalSkipMixin`
    -  several conditional operators in :mod:`~sai_airflow_plugins.operators.conditional_operators` and
       :mod:`~sai_airflow_plugins.sensors.conditional_sensors`

0.1.1
-----

*(2021-07-05)*

- Added parameters `use_sudo`, `sudo_user` and `strip_stdout` to
  :class:`~sai_airflow_plugins.operators.fabric_operator.FabricOperator`
- Parameter `get_pty` in :class:`~sai_airflow_plugins.operators.fabric_operator.FabricOperator` is no longer
  automatically set to True when running a sudo command

0.1.2
-----

*(2021-07-05)*

- Fixed: parameters weren't correctly supplied to Fabric's run and sudo functions in
  :class:`~sai_airflow_plugins.operators.fabric_operator.FabricOperator`

0.1.3
-----

*(2021-07-06)*

- Fixed: removed http extra in setup.py requirements because this is incompatible with airflow 1.10.x

0.1.4
-----

*(2022-02-21)*

- Fixed: in FabricOperator, remove the sudo prompt from stdout when doing a sudo command in a pty

0.1.5
-----

*(2022-02-21)*

- Fixed: only test on python 3.8 with airflow 2.2.3 due to airflow's strict contraint files
