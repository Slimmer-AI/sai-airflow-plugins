import json
import unittest
from unittest.mock import patch

from airflow.exceptions import AirflowException
from faker import Faker

from sai_airflow_plugins.hooks.mattermost_webhook_hook import MattermostWebhookHook

faker = Faker()


class TestMattermostWebhookHook(unittest.TestCase):

    def test_http_conn_id_or_webhook_token_required(self):
        """
        Test that the hook constructor requires either a http_conn_id or a webhook_token
        """
        with self.assertRaises(AirflowException):
            MattermostWebhookHook()

        with patch(f"{__name__}.MattermostWebhookHook.get_connection"):
            MattermostWebhookHook(http_conn_id=faker.pystr())

        MattermostWebhookHook(webhook_token=faker.url())

    def test_execute(self):
        """
        Test that the hook execute method calls `HttpHook.run` with the correct endpoint, headers, options and
        json body
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
        hook = MattermostWebhookHook(**kwargs)

        expected_body = dict(
            text=kwargs["message"],
            attachments=kwargs["attachments"],
            props=kwargs["props"],
            type=kwargs["post_type"],
            channel=kwargs["channel"],
            username=kwargs["username"],
            icon_emoji=kwargs["icon_emoji"],
            icon_url=kwargs["icon_url"],
        )
        expected_extra_options = dict(
            **kwargs["extra_options"],
            proxies=dict(https=kwargs["proxy"])
        )

        with patch(f"{__name__}.MattermostWebhookHook.run") as mock_run:
            hook.execute()

            mock_run.assert_called_once()
            args = mock_run.call_args[1]
            self.assertEqual(args["endpoint"], kwargs["webhook_token"])
            self.assertEqual(args["headers"], {"Content-type": "application/json"})
            self.assertEqual(json.loads(args["data"]), expected_body)
            self.assertEqual(args["extra_options"], expected_extra_options)
