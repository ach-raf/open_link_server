import requests
from bs4 import BeautifulSoup


def get_title_from_url(url):
    # Use requests to get the contents
    r = requests.get(url)
    # Get the text of the contents
    html_content = r.text
    # Convert the html content into a beautiful soup object
    soup = BeautifulSoup(html_content, 'lxml')
    return soup.title.string
