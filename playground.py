from feedparser_functions import get_feed_data, get_feed_info
from json_functions import pretty_print, write_json

rss_links = ["https://www.thehindu.com/feeder/default.rss","http://indianexpress.com/feed"]

all_links = []

for link in rss_links:
    item ={}
    feed_info = get_feed_info(link)
    feed_data = get_feed_data(link)
    item['rss_name'] = link
    item['feed_info'] = feed_info
    item['feed_data'] = feed_data

    all_links.append(item)

write_json(all_links, 'rss_feed.json')

