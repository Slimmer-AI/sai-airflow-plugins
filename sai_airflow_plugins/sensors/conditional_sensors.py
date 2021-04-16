from airflow.contrib.sensors.bash_sensor import BashSensor
from airflow.contrib.sensors.python_sensor import PythonSensor

from sai_airflow_plugins.operators.conditional_skip_mixin import ConditionalSkipMixin
from sai_airflow_plugins.sensors.fabric_sensor import FabricSensor


class ConditionalBashSensor(ConditionalSkipMixin, BashSensor):
    """
    Conditional bash sensor.

    .. seealso:: :class:`~sai_airflow_plugins.operators.conditional_skip_mixin.ConditionalSkipMixin` and
                 :class:`~airflow.contrib.sensors.bash_sensor.BashSensor`
    """
    template_fields = BashSensor.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#ede4ff"


class ConditionalPythonSensor(ConditionalSkipMixin, PythonSensor):
    """
    Conditional python sensor.

    .. seealso:: :class:`~sai_airflow_plugins.operators.conditional_skip_mixin.ConditionalSkipMixin` and
                 :class:`~airflow.contrib.sensors.bash_sensorPythonSensor`
    """
    template_fields = PythonSensor.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#ffebff"


class ConditionalFabricSensor(ConditionalSkipMixin, FabricSensor):
    """
    Conditional Fabric sensor.

    .. seealso:: :class:`~sai_airflow_plugins.operators.conditional_skip_mixin.ConditionalSkipMixin` and
                 :class:`~sai_airflow_plugins.sensors.fabric_sensor.FabricSensor`
    """
    template_fields = FabricSensor.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#e6f2eb"
