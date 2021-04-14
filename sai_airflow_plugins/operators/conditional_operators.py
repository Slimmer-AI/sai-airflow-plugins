from airflow.operators.bash_operator import BashOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python_operator import PythonOperator

from sai_airflow_plugins.operators.conditional_skip_mixin import ConditionalSkipMixin
from sai_airflow_plugins.operators.fabric_operator import FabricOperator


class ConditionalBashOperator(ConditionalSkipMixin, BashOperator):
    """
    Conditional bash operator.

    .. seealso:: :class:`ConditionalSkipMixin` and :class:`BashOperator`
    """
    template_fields = BashOperator.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#ede4ff"


class ConditionalPythonOperator(ConditionalSkipMixin, PythonOperator):
    """
    Conditional python operator.

    .. seealso:: :class:`ConditionalSkipMixin` and :class:`PythonOperator`
    """
    template_fields = PythonOperator.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#ffebff"


class ConditionalTriggerDagRunOperator(ConditionalSkipMixin, TriggerDagRunOperator):
    """
    Conditional trigger DAG run operator.

    .. seealso:: :class:`ConditionalSkipMixin` and :class:`TriggerDagRunOperator`
    """
    template_fields = TriggerDagRunOperator.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#efeaff"


class ConditionalFabricOperator(ConditionalSkipMixin, FabricOperator):
    """
    Conditional Fabric operator.

    .. seealso:: :class:`ConditionalSkipMixin` and :class:`FabricOperator`
    """
    template_fields = FabricOperator.template_fields + ConditionalSkipMixin.template_fields
    ui_color = "#feffe5"
