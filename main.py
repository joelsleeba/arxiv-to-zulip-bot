import os
import requests
import time
import zulip
from datetime import datetime, timedelta, timezone

# Define your Zulip credentials
ZULIP_EMAIL = os.environ.get('ZULIP_EMAIL')
ZULIP_STREAM_NAME = 'Research'

# Define arXiv categories
ARXIV_CATEGORIES = ["math.OA", "math.FA"]

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
def fetch_latest_articles(category_list):
    url = f"http://export.arxiv.org/api/query?search_query=cat:{category_list}&sortBy=lastUpdatedDate&sortOrder=descending&start=0&max_result=15"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.text.split("<entry>")
        # Skip the first element which is not an article
        for article in articles[1:]:
            updated_str = article.split("<updated>")[1].split("</updated>")[0]
            updated_time = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%S%z")
            current_time = datetime.now(timezone.utc)
            if current_time - updated_time <= timedelta(hours=24):
                title = article.split("<title>")[1].split("</title>")[0].replace('$^{\\ast}$', '* ').replace('$^*$', '* ').replace('$^*$', '* ').replace("$", "$$").replace("\n", " ")
                author_list = article.split("<author>")[1:] # list of authors
                authors = ", ".join([name.split("<name>")[1].split("</name>")[0] for name in author_list])
                summary = article.split("<summary>")[1].split("</summary>")[0].replace('$^\{ast}$', '* ').replace('$^*$', '* ').replace("$", "$$").replace("\n  ", "😉").replace("\n", " ").replace("😉", "\n  ")


                link = article.split('<link href="')[1].split('"')[0]
                category= article.split('<category term="')[1].split('"')[0]
                message = f"\n**{title}**\n*{authors}*\n\n{summary}\n{category}: {link}"
                send_zulip_message(message)
                # print(message)
    else:
        print(response.text)

# Main function to check for new articles periodically
def main():
    category = '+OR+cat:'.join(ARXIV_CATEGORIES) # Check https://info.arxiv.org/help/rss.html#subscribe-by-multiple-categories
    fetch_latest_articles(category)

if __name__ == "__main__":
    main()
