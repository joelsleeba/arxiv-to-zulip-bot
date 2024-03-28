import os
import requests
import time
import zulip

# Define your Zulip credentials
ZULIP_EMAIL = os.environ.get('ZULIP_EMAIL')
ZULIP_STREAM_NAME = 'Research'

# Define arXiv categories
ARXIV_CATEGORIES = ["math.OA", "quant-ph", "math.FA"]

# Function to send a message to Zulip
def send_zulip_message(content):
    client = zulip.Client(email=ZULIP_EMAIL, client='test-github-client/0.1')
    data = {
        "type": "stream",
        "to": ZULIP_STREAM_NAME,
        "topic": "New arXiv articles",
        "content": content }
    client.send_message(data)

# Function to fetch latest articles from arXiv
def fetch_latest_articles(category):
    url = f"http://export.arxiv.org/rss/{category}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.text.split("<item>")
        # Skip the first element which is not an article
        for article in articles[1:]:
            title = article.split("<title>")[1].split("</title>")[0].replace('$^{\\ast}$', '* ').replace('$^*$', '* ').replace('$^*$', '* ').replace("$", "$$")
            creator = article.split("<dc:creator>")[1].split("</dc:creator>")[0]
            summary = article.split("Abstract: ")[1].split("</description>")[0].replace('$^\{ast}$', '* ').replace('$^*$', '* ').replace("$", "$$")
            link = article.split("<link>")[1].split("</link>")[0]
            message = f"\n**{title}**\n*{creator}*\n\n{summary}\n{category} : {link}"
            send_zulip_message(message)

# Main function to check for new articles periodically
def main():
    for category in ARXIV_CATEGORIES:
        fetch_latest_articles(category)

if __name__ == "__main__":
    main()
