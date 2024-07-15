from urllib.parse import quote
from bs4 import BeautifulSoup

def construct_search_url(query):
    website = "https://www.perplexity.ai/search"
    formatted_query = quote(query)
    search_url = f"{website}?q={formatted_query}"
    return search_url

def contruct_news_html_email_content(news, direct_link):
    styles = """
    <style>
        .news-unit { margin-bottom: 30px; }
        .title { color: #000080; margin-bottom: 5px;}
        .description { margin: 0px 0px 10px 0px; }
        hr { border: 1px solid #f1f1f1; }
    </style>
    """
    
    html_structure = f"""
    <html>
        <head>{styles}</head>
        <body></body>
    </html>
    """
    
    soup = BeautifulSoup(html_structure, "html.parser")
    body = soup.body
    news_items_container = soup.new_tag("div", attrs={"class": "news-items-container"})
    body.append(news_items_container)
    for news_item in news:
        div = soup.new_tag("div", attrs={"class": "news-unit"})
        news_items_container.append(div)
        h2 = soup.new_tag("h2", attrs={"class": "title"})
        h2.string = news_item['title']
        div.append(h2)
        p = soup.new_tag("p", attrs={"class": "description"})
        p.string = news_item['description']
        div.append(p)
        hr = soup.new_tag("hr")
        div.append(hr)
    perplexity_link_container = soup.new_tag("div", attrs={"class": "perplexity-link-container"})
    body.append(perplexity_link_container)
    perplexity_link = soup.new_tag("a", href=direct_link)
    perplexity_link.string = "View on Perplexity"
    perplexity_link_container.append(perplexity_link)
    
    return str(soup)