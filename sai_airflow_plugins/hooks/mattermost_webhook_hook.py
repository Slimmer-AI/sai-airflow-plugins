import json
from typing import Optional, List, Dict, Any

from airflow.exceptions import AirflowException
from airflow.hooks.http_hook import HttpHook


class MattermostWebhookHook(HttpHook):
    """
    This hook allows you to post messages to Mattermost using incoming webhooks.
    It takes either a Mattermost webhook token directly or a connection that has a Mattermost webhook token.
    If both are supplied, http_conn_id will be used as base_url, and webhook_token will be taken as endpoint,
    the relative path of the url.

    Each Mattermost webhook token can be pre-configured to use a specific channel, username and icon. You can override
    these defaults in this hook.

    This hook is based on `airflow.contrib.hooks.SlackWebhookHook` as the Mattermost interface is largely similar
    to that of Slack.

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
        super().__init__(http_conn_id=http_conn_id, *args, **kwargs)
        self.webhook_token = self._get_token(webhook_token, http_conn_id)
        self.message = message
        self.attachments = attachments
        self.props = props
        self.post_type = post_type
        self.channel = channel
        self.username = username
        self.icon_emoji = icon_emoji
        self.icon_url = icon_url
        self.proxy = proxy
        self.extra_options = extra_options or {}

    def _get_token(self, token: str, http_conn_id: str) -> str:
        """
        Given either a manually set token or a conn_id, return the webhook_token to use.

        :param token: The manually provided token
        :param http_conn_id: The conn_id provided
        :return: webhook_token to use
        """
        if token:
            return token
        elif http_conn_id:
            conn = self.get_connection(http_conn_id)
            extra = conn.extra_dejson
            return extra.get("webhook_token", "")
        else:
            raise AirflowException("Cannot get webhook token: no valid Mattermost webhook token nor conn_id supplied")

    def _build_mattermost_message(self) -> str:
        """
        Construct the Mattermost message. All relevant parameters are combined here to a valid Mattermost json body.

        :return: Mattermost JSON body to send
        """
        cmd = {}

        if self.channel:
            cmd["channel"] = self.channel
        if self.username:
            cmd["username"] = self.username
        if self.icon_emoji:
            cmd["icon_emoji"] = self.icon_emoji
        if self.icon_url:
            cmd["icon_url"] = self.icon_url
        if self.attachments:
            cmd["attachments"] = self.attachments
        if self.props:
            cmd["props"] = self.props
        if self.post_type:
            cmd["type"] = self.post_type

        cmd["text"] = self.message
        return json.dumps(cmd)

    def execute(self):
        """
        Execute the Mattermost webhook call
        """

        if self.proxy:
            # we only need https proxy for Mattermost, as the endpoint is https
            self.extra_options.update({"proxies": {"https": self.proxy}})

        mattermost_message = self._build_mattermost_message()
        self.run(endpoint=self.webhook_token,
                 data=mattermost_message,
                 headers={"Content-type": "application/json"},
                 extra_options=self.extra_options)
