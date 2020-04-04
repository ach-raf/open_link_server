import requests
from bs4 import BeautifulSoup
from youtube_info import get_youtube_info


def get_title_from_url(url):
    if 'youtu' in url:
        return get_youtube_info(url)
    else:
        # Use requests to get the contents
        r = requests.get(url)
        # Get the text of the contents
        html_content = r.text
        # Convert the html content into a beautiful soup object
        soup = BeautifulSoup(html_content, 'lxml')
        return soup.title.string
