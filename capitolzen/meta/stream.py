from stream_django.managers import FeedManager as DefaultFeedManager
from stream_django.client import stream_client


class FeedManager(DefaultFeedManager):
    """

    """
    def get_group_feed(self, group_id):
        return stream_client.feed('group', group_id)
