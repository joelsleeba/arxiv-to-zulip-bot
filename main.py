import os
import zulip
import re
import feedparser
from datetime import datetime

# Define your Zulip credentials
ZULIP_EMAIL = os.environ.get('ZULIP_EMAIL')
ZULIP_STREAM_NAME = 'articles'
ZULIP_TOPIC_NAME = 'New arXiv articles'

# Define arXiv categories
ARXIV_CATEGORIES = ["math.OA", "math.FA"]

# Function to send a message to Zulip


def send_zulip_message(content):
    client = zulip.Client(email=ZULIP_EMAIL, client='test-github-client/0.1')
    data = {
        "type": "stream",
        "to": ZULIP_STREAM_NAME,
        "topic": ZULIP_TOPIC_NAME,
        "content": content}
    client.send_message(data)

# Get the url of the last article update sent to the stream


def last_article_update_link():
    client = zulip.Client(
        email=ZULIP_EMAIL, client='arxiv-bot-github-actions/0.1')
    request: Dict[str, Any] = {
        "anchor": "newest",
        "num_before": 1,
        "num_after": 0,
        "narrow": [
            {"operator": "sender", "operand": ZULIP_EMAIL},
            {"operator": "stream", "operand": ZULIP_STREAM_NAME},
            {"operator": "topic", "operand": ZULIP_TOPIC_NAME},
        ],
        "apply_markdown": False
    }
    response = client.get_messages(request)
    if response['result'] == "success":
        messages = response["messages"]
        if messages:
            latest_message = messages[0]
            latest_message_content = latest_message["content"]
            url_pattern = r'\[.*?\]\((.*?)\)'
            latest_arxiv_link = re.findall(
                url_pattern, latest_message_content)[0]
            return latest_arxiv_link
        else:
            return None
    else:
        print("Failed to retrieve message or No previous messages")
        return None

# Function to fetch latest articles from arXiv


def update_zulip_stream(category_list):
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category_list}&sortBy=lastUpdatedDate&sortOrder=descending&start=0&max_result=100"
    d = feedparser.parse(url)
    last_updated_article_link = last_article_update_link()
    print(f"last updated article was : {last_updated_article_link}")
    if d.status == 200:
        articles = d.entries
        # To avoid the case when not having an article ends up not getting to the execution part of the for loop
        flag = True if last_updated_article_link else False
        # Skip the first element which is not an article
        # This is to get the list in ascending order by time
        for article in articles[::-1]:
            link = article.link
            if flag:
                if link == last_updated_article_link:
                    flag = False
                continue
            title = article.title.replace('$^{\\ast}$', '* ').replace(
                '$^*$', '* ').replace('$^*$', '* ').replace("$", "$$").replace("\n", " ")
            author_list = [i.name for i in article.authors]  # list of authors
            authors = ", ".join(author_list)
            summary = article.summary.replace('$^{\\ast}$', '* ').replace(
                '$^*$', '* ').replace("$", "$$").replace("\n  ", "😉").replace("\n", " ").replace("😉", "\n  ")
            categories = ", ".join([i.term for i in article.tags])
            message = f"\n**[{title}]({link})**\n*{authors}*\n\n{summary}\n\n*{categories}*"
            print(message)
            send_zulip_message(message)
    else:
        print()

# Main function to check for new articles periodically


def main():
    # Check https://info.arxiv.org/help/rss.html#subscribe-by-multiple-categories
    category = '+OR+cat:'.join(ARXIV_CATEGORIES)
    update_zulip_stream(category)


if __name__ == "__main__":
    main()
