import unittest
from unittest.mock import patch

from faker import Faker

from sai_airflow_plugins.operators.mattermost_webhook_operator import MattermostWebhookOperator

TEST_TASK_ID = "test_mattermost_webhook_operator"

faker = Faker()


class TestMattermostWebhookOperator(unittest.TestCase):

    def test_execute(self):
        """
        Test that execute creates a `MattermostWebhookHook` with all parameters and calls its execute method
        """
        kwargs = dict(
            webhook_token=faker.url(),
            message=faker.text(),
            attachments=[faker.pydict(value_types=[str, int, bool]), faker.pydict(value_types=[str, int, bool])],
            props=faker.pydict(value_types=[str, int, bool]),
            post_type=faker.pystr(),
            channel=faker.pystr(),
            username=faker.user_name(),
            icon_emoji=faker.pystr(),
            icon_url=faker.url(),
            proxy=faker.url(),
            extra_options={"timeout": faker.pyint(), "allow_redirects": faker.pybool()}
        )
        op = MattermostWebhookOperator(task_id=TEST_TASK_ID, **kwargs)

        with patch("sai_airflow_plugins.operators.mattermost_webhook_operator.MattermostWebhookHook.execute"
                   ) as mock_hook_execute:
            op.execute(context={})
            mock_hook_execute.assert_called_once()

            for arg_name, arg_val in kwargs.items():
                self.assertEqual(getattr(op.hook, arg_name), arg_val)
