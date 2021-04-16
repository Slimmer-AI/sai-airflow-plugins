import unittest
from unittest.mock import patch

from airflow.exceptions import AirflowSkipException
from airflow.models.baseoperator import BaseOperator
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from faker import Faker

from sai_airflow_plugins.operators.conditional_skip_mixin import ConditionalSkipMixin

TEST_TASK_ID = "test_conditional_operator"

faker = Faker()


class ConditionalTestOperator(ConditionalSkipMixin, BaseOperator):
    pass


class ConditionalTestSensor(ConditionalSkipMixin, BaseSensorOperator):
    pass


class TestConditionalOperator(unittest.TestCase):

    def test_condition_true(self):
        """
        Test that the superclass execute is called when the callable evaluates to True
        """
        with patch(f"{__name__}.BaseOperator.execute") as mock_super_execute:
            op = ConditionalTestOperator(task_id=TEST_TASK_ID, condition_callable=lambda: True)
            op.execute(context={})
            mock_super_execute.assert_called_once()

    def test_condition_false(self):
        """
        Test that execute raises `AirflowSkipException` when the callable evaluates to False
        """
        with patch(f"{__name__}.BaseOperator.execute") as mock_super_execute:
            with self.assertRaises(AirflowSkipException):
                op = ConditionalTestOperator(task_id=TEST_TASK_ID, condition_callable=lambda: False)
                op.execute(context={})
                mock_super_execute.assert_not_called()

    def test_context_and_parameters(self):
        """
        Test that execute correctly supplies the callable with parameters and context if added
        """
        def test_callable(*args, **kwargs):
            self.assertEqual(args, (1,))
            self.assertEqual(kwargs, {"my_param": 2, "my_context_param": 3})
            return True

        with patch(f"{__name__}.BaseOperator.execute"):
            op = ConditionalTestOperator(task_id=TEST_TASK_ID,
                                         condition_callable=test_callable,
                                         condition_args=[1],
                                         condition_kwargs={"my_param": 2},
                                         condition_provide_context=True)
            op.execute({"my_context_param": 3})


class TestConditionalSensor(unittest.TestCase):

    def test_condition_true(self):
        """
        Test that the superclass poke is called when the callable evaluates to True
        """
        with patch(f"{__name__}.BaseSensorOperator.poke") as mock_super_poke:
            op = ConditionalTestSensor(task_id=TEST_TASK_ID, condition_callable=lambda: True)
            op.poke(context={})
            mock_super_poke.assert_called_once()

    def test_condition_false(self):
        """
        Test that poke raises `AirflowSkipException` when the callable evaluates to False
        """
        with patch(f"{__name__}.BaseSensorOperator.poke") as mock_super_poke:
            with self.assertRaises(AirflowSkipException):
                op = ConditionalTestSensor(task_id=TEST_TASK_ID, condition_callable=lambda: False)
                op.poke(context={})
                mock_super_poke.assert_not_called()

    def test_context_and_parameters(self):
        """
        Test that poke correctly supplies the callable with parameters and context if added
        """
        def test_callable(*args, **kwargs):
            self.assertEqual(args, (1,))
            self.assertEqual(kwargs, {"my_param": 2, "my_context_param": 3})
            return True

        with patch(f"{__name__}.BaseSensorOperator.poke"):
            op = ConditionalTestSensor(task_id=TEST_TASK_ID,
                                       condition_callable=test_callable,
                                       condition_args=[1],
                                       condition_kwargs={"my_param": 2},
                                       condition_provide_context=True)
            op.poke({"my_context_param": 3})
