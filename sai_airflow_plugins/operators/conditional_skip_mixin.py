from typing import Callable, Optional, Iterable, Dict

from airflow.exceptions import AirflowSkipException
from airflow.utils.decorators import apply_defaults


class ConditionalSkipMixin(object):
    """
    Mixin for making operators and sensors conditional. If the condition evaluates to True the operator or sensor
    executes normally, otherwise it skips the task.

    Note that you should correctly set the `template_field` in a derived class to include both the operator's
    and this mixin's templated fields. Example:

        class MyConditionalOperator(ConditionalSkipMixin, MyOperator):
            template_fields = MyOperator.template_fields + ConditionalSkipMixin.template_fields

    :param condition_callable: A callable that should evaluate to a truthy or falsy value to execute or skip the
                               task respectively. Note that Airflow's context is also passed as keyword arguments so
                               you need to define `**kwargs` in your function header. (templated)
    :param condition_kwargs: a dictionary of keyword arguments that will get unpacked in `condition_callable`.
                             (templated)
    :param condition_args: a list of positional arguments that will get unpacked in `condition_callable`. (templated)
    :param condition_provide_context: if set to true, Airflow will pass a set of keyword arguments that can be used in
                                      your condition callable. This set of kwargs correspond exactly to what you can
                                      use in your jinja templates. For this to work, you need to define `**kwargs` in
                                      your function header.
    """
    template_fields = ("condition_callable", "condition_args", "condition_kwargs")

    @apply_defaults
    def __init__(self,
                 condition_callable: Callable = False,
                 condition_args: Optional[Iterable] = None,
                 condition_kwargs: Optional[Dict] = None,
                 condition_provide_context: Optional[bool] = False,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.condition_callable = condition_callable
        self.condition_args = condition_args or []
        self.condition_kwargs = condition_kwargs or {}
        self.condition_provide_context = condition_provide_context
        self._condition_evaluated = False
        self._condition_value = None

    def execute(self, context: Dict):
        """
        If the condition evaluates to True execute the superclass `execute` method, otherwise skip the task.

        :param context: Context dict provided by airflow
        """
        if self._get_evaluated_condition_or_skip(context):
            super().execute(context)

    def poke(self, context: Dict) -> bool:
        """
        If the condition evaluates to True execute the superclass `poke` method, otherwise skip the task.

        :param context: Context dict provided by airflow
        :return: The result of the superclass `poke` method
        """
        if self._get_evaluated_condition_or_skip(context):
            return super().poke(context)

    def _get_evaluated_condition_or_skip(self, context: Dict):
        """
        Lazily evaluates `condition_callable` and raises `AirflowSkipException` if it's falsy.
        This is done because the `poke` method of a sensor may call the `execute` method as well.

        :param context: Context dict provided by airflow
        :return: The (cached) result of `condition_callable` if truthy, otherwise raises `AirflowSkipException`
        """
        if not self._condition_evaluated:

            if self.condition_provide_context:
                # Merge airflow's context and the callable's kwargs
                context.update(self.condition_kwargs)
                self.condition_kwargs = context

            self._condition_value = self.condition_callable(*self.condition_args, **self.condition_kwargs)

        if self._condition_value:
            return self._condition_value
        else:
            raise AirflowSkipException(
                f"Condition callable {self.condition_callable.__name__} evaluated to False. Skipping this task."
            )
