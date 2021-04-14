from typing import Optional, List, Dict, Any

from airflow.operators.http_operator import SimpleHttpOperator
from airflow.utils.decorators import apply_defaults

from sai_airflow_plugins.hooks.mattermost_webhook_hook import MattermostWebhookHook


class MattermostWebhookOperator(SimpleHttpOperator):
    """
    This operator allows you to post messages to Mattermost using incoming webhooks.
    It takes either a Mattermost webhook token directly or a connection that has a Mattermost webhook token.
    If both are supplied, http_conn_id will be used as base_url, and webhook_token will be taken as endpoint,
    the relative path of the url.

    Each Mattermost webhook token can be pre-configured to use a specific channel, username and icon. You can override
    these defaults in this operator.

    This operator is based on `airflow.contrib.operators.SlackWebhookOperator` as the Mattermost interface is largely
    similar to that of Slack.

    :param http_conn_id: connection that optionally has a Mattermost webhook token in the extra field
    :param webhook_token: Mattermost webhook token. If http_conn_id isn't supplied this should be the full webhook url.
    :param message: The message you want to send on Mattermost
    :param attachments: The attachments to send on Mattermost. Should be a list of dictionaries representing
                        Mattermost attachments.
    :param props: The props to send on Mattermost. Should be a dictionary representing Mattermost props.
    :param post_type: Sets an optional Mattermost post type, mainly for use by plugins. If supplied, must begin with
                      "custom_"
    :param channel: The channel the message should be posted to
    :param username: The username to post with
    :param icon_emoji: The emoji to use as icon for the user posting to Mattermost
    :param icon_url: The icon image URL string to use in place of the default icon.
    :param proxy: Proxy to use to make the Mattermost webhook call
    :param extra_options: Extra options for http hook
    """

    template_fields = ["webhook_token", "message", "attachments", "props", "post_type", "channel", "username",
                       "proxy", "extra_options"]

    @apply_defaults
    def __init__(self,
                 http_conn_id: Optional[str] = None,
                 webhook_token: Optional[str] = None,
                 message: str = "",
                 attachments: Optional[List[Dict[str, Any]]] = None,
                 props: Optional[Dict[str, Any]] = None,
                 post_type: Optional[str] = None,
                 channel: Optional[str] = None,
                 username: Optional[str] = None,
                 icon_emoji: Optional[str] = None,
                 icon_url: Optional[str] = None,
                 proxy: Optional[str] = None,
                 extra_options: Optional[Dict[str, Any]] = None,
                 *args,
                 **kwargs):
        super().__init__(endpoint=webhook_token, *args, **kwargs)
        self.http_conn_id = http_conn_id
        self.webhook_token = webhook_token
        self.message = message
        self.attachments = attachments
        self.props = props
        self.post_type = post_type
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.icon_url = icon_url
        self.proxy = proxy
        self.hook = None
        self.extra_options = extra_options

    def execute(self, context: Dict):
        """
        Call the MattermostWebhookHook to post the provided Mattermost message
        """
        self.hook = MattermostWebhookHook(
            self.http_conn_id,
            self.webhook_token,
            self.message,
            self.attachments,
            self.props,
            self.post_type,
            self.channel,
            self.username,
            self.icon_emoji,
            self.icon_url,
            self.proxy,
            self.extra_options
        )
        self.hook.execute()
