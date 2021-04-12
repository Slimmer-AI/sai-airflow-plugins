from airflow.plugins_manager import AirflowPlugin

from sai_airflow_plugins.hooks.fabric_hook import FabricHook
from sai_airflow_plugins.operators.conditional_operators import ConditionalBashOperator, ConditionalFabricOperator, \
    ConditionalPythonOperator, ConditionalTriggerDagRunOperator
from sai_airflow_plugins.operators.fabric_operator import FabricOperator
from sai_airflow_plugins.sensors.conditional_sensors import ConditionalBashSensor, ConditionalPythonSensor, \
    ConditionalFabricSensor
from sai_airflow_plugins.sensors.fabric_sensor import FabricSensor


class SaiAirflowPlugin(AirflowPlugin):
    """
    Main Slimmer AI Airflow plugins class. It exposes the plugins in the following airflow packages:
      * airflow.hooks.sai_airflow_plugins.*
      * airflow.operators.sai_airflow_plugins.*
      * airflow.sensors.sai_airflow_plugins.*
    """
    name = "sai_airflow_plugins"
    hooks = [FabricHook]
    operators = [FabricOperator,
                 ConditionalBashOperator,
                 ConditionalPythonOperator,
                 ConditionalTriggerDagRunOperator,
                 ConditionalFabricOperator]
    sensors = [FabricSensor,
               ConditionalBashSensor,
               ConditionalPythonSensor,
               ConditionalFabricSensor]
