import os
import requests
import time

# Define your Zulip credentials
ZULIP_API_URL = os.environ.get('ZULIP_API_URL')
ZULIP_EMAIL = os.environ.get('ZULIP_EMAIL')
ZULIP_API_KEY = os.environ.get('ZULIP_API_KEY')
ZULIP_STREAM_NAME = os.environ.get('ZULIP_STREAM_NAME')

# Define arXiv categories
ARXIV_CATEGORIES = ["math.OA", "math.FA"]

# Function to send a message to Zulip
def send_zulip_message(content):
    data = {
        "type": "stream",
        "to": ZULIP_STREAM_NAME,
        "subject": "New arXiv Article",
        "content": content }
    response = requests.post(
        f"{ZULIP_API_URL}/messages",
        auth=(ZULIP_EMAIL, ZULIP_API_KEY),
        json=data
    )
    print(response.text)

# Function to fetch latest articles from arXiv
def fetch_latest_articles(category):
    url = f"http://export.arxiv.org/rss/{category}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.text.split("<item>")
        # Skip the first element which is not an article
        for article in articles[1:]:
            title = article.split("<title>")[1].split("</title>")[0]
            link = article.split("<link>")[1].split("</link>")[0]
            creator = article.split("<dc:creator>")[1].split("</dc:creator>")[0]
            summary = article.split("Abstract: ")[1].split("</description>")[0].replace("$", "$$")
            message = f"\n**{title}**\n*{creator}*\n\n{summary}\n{category}:{link}"
            send_zulip_message(message)

# Main function to check for new articles periodically
def main():
    for category in ARXIV_CATEGORIES:
        fetch_latest_articles(category)

if __name__ == "__main__":
    main()
