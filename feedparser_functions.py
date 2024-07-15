import feedparser


def get_feed_info(feed_url):
    NewsFeed = feedparser.parse(feed_url)
    feed_info = NewsFeed.feed
    return feed_info

def get_feed_data(feed_url):
    NewsFeed = feedparser.parse(feed_url)
    entries = []
    for entry in NewsFeed.entries:
        item = entry
        entries.append(item)
    return entries