import os
import requests
import time
import zulip
import re
from datetime import datetime, timedelta, timezone

# Define your Zulip credentials
ZULIP_EMAIL = os.environ.get('ZULIP_EMAIL')
ZULIP_STREAM_NAME = 'Research'
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
        "content": content }
    client.send_message(data)

# Get the url of the last article update sent to the stream
def last_article_update_link():
    client = zulip.Client(email=ZULIP_EMAIL, client='test-github-client/0.1')
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
            url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
            latest_arxiv_link = re.findall(url_pattern, latest_message_content)[0]
            return latest_arxiv_link
        else:
            return None
    else:
        print(f"Failed to retrieve message: {response.text}")
        return None

# Function to fetch latest articles from arXiv
def update_zulip_stream(category_list):
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category_list}&sortBy=lastUpdatedDate&sortOrder=descending&start=0&max_result=15"
    response = requests.get(url)
    last_updated_article_link = last_article_update_link()
    if response.status_code == 200:
        articles = response.text.split("<entry>")
        flag = True  #Used to skip articles until the last_updated_article_link is reached
        # Skip the first element which is not an article
        for article in articles[1:][::-1]: #This is to get the list in ascending order by time
            link = article.split('<link href="')[1].split('"')[0]
            if flag:
                if link == last_updated_article_link:
                    flag = False
                continue
            title = article.split("<title>")[1].split("</title>")[0].replace('$^{\\ast}$', '* ').replace('$^*$', '* ').replace('$^*$', '* ').replace("$", "$$").replace("\n", " ")
            author_list = article.split("<author>")[1:] # list of authors
            authors = ", ".join([name.split("<name>")[1].split("</name>")[0] for name in author_list])
            summary = article.split("<summary>")[1].split("</summary>")[0].replace('$^\{ast}$', '* ').replace('$^*$', '* ').replace("$", "$$").replace("\n  ", "😉").replace("\n", " ").replace("😉", "\n  ")
            category= article.split('<category term="')[1].split('"')[0]
            message = f"\n**{title}**\n*{authors}*\n\n{summary}\n{category}: {link}"
            send_zulip_message(message)
    else:
        print(response.text)

# Main function to check for new articles periodically
def main():
    category = '+OR+cat:'.join(ARXIV_CATEGORIES) # Check https://info.arxiv.org/help/rss.html#subscribe-by-multiple-categories
    update_zulip_stream(category)

if __name__ == "__main__":
    main()
