from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from time import sleep
from database_utils import insert_data
import requests, os, sqlite3
from datetime import datetime


class NewsScraper:
    def __init__(self, provider):
        self.provider = provider
        self.urls = self.scrape(provider)
        self.articles = self.parse(provider, self.urls)
        self.insert(provider, self.articles)

    def scrape_url(provider, url):
        page = requests.get(url)

        # Check if the page was successfully downloaded
        if page.status_code == 200:
            # Parse the HTML document
            soup = BeautifulSoup(page.content, "html.parser")
        else:  # If the page was not successfully downloaded
            # Print the error code
            print("Page status code:", page.status_code)
            # Return an empty list
            return []

        # Find all the articles on the page
        articles = soup.find_all("article")

    def scrape(provider):
        # Define the URL of the RSS feed
        rss_url = "https://www.theonion.com/rss"

        # Use a ThreadPoolExecutor to parallelize the scraping process
        with ThreadPoolExecutor(max_workers=10) as executor:
            urls = list(executor.map(scrape_url, [rss_url]))

        # Flatten the list of URLs
        urls = [url for sublist in urls for url in sublist]

        # Return the URLs
        return urls
