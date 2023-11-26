from datetime import datetime

import sqlite3
import sys
from flask import Flask, request, jsonify
from newspaper import Article
from GoogleNews import GoogleNews
from newsapi import NewsApiClient
import logging
import requests
import readtime

# from recommenders.models.deeprec.deeprec_utils import download_deeprec_resources
# from recommenders.models.newsrec.newsrec_utils import prepare_hparams
# from recommenders.models.newsrec.models.naml import NAMLModel
# from recommenders.models.newsrec.io.mind_all_iterator import MINDAllIterator

from database_utils import db_path, get_articles, run_query, table_exists
from scraper import NewsScraper, Provider

# Configure the logging level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

# Configure the GoogleNews client
googlenews = GoogleNews(lang="en")

# Configure the NewsAPI client
newsapi = NewsApiClient(api_key="13328281630540aaa6c2750b76b5ee12")

# Connect to the SQLite database
conn = sqlite3.connect(db_path(), check_same_thread=False)

# Initialize the Flask application
flask_app = Flask(__name__)


# Error handler for incorrect URL
@flask_app.errorhandler(ValueError)
def value_error_handler(e):
    logging.error(e)
    return jsonify(error=str(e)), 404


# Define a GET method for "top" endpoint
@flask_app.route("/top", methods=["GET"])
def top():
    # Try-except block to handle errors
    try:
        # Get the country string from the query parameters
        country = request.args.get("country")

        # Get the top headlines from NewsAPI
        logging.info("Getting top headlines for %s", country)
        top_headlines = newsapi.get_top_headlines(country=country, language="en")
        result = top_headlines["articles"]

        # Return the results as a JSON response
        return jsonify(result)
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "feed" endpoint
@flask_app.route("/feed", methods=["GET"])
def feed():
    # Try-except block to handle errors
    try:
        # Get articles from the database
        articles = get_articles(conn)

        # Return the feed as a JSON response
        return jsonify(
            {
                "status": "ok",
                "totalResults": len(articles),
                "articles": clean_articles_db(articles),
            }
        )

    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "scrape" endpoint
@flask_app.route("/scrape", methods=["GET"])
def scrape():
    # Try-except block to handle errors
    try:
        scraper = NewsScraper(Provider.GMANews)
        scraper.scrape()

        # Execute the scraper
        # exec(open("scraper.py").read())

        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "search" endpoint
@flask_app.route("/search", methods=["GET"])
def search():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        query = request.args.get("q")
        # Get the top 5 results from Google News
        googlenews.search(query)
        result = clean_articles(googlenews.result())

        # Clear GoogleNews results
        googlenews.clear()

        # Return the results as a JSON response
        return jsonify(result[:5])
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Clean the articles from db
def clean_articles_db(articles):
    cleaned_articles = []

    # date, category, source, title, author, url, body, image_url, read_time

    for article in articles:
        cleaned_articles.append(
            {
                "date": article[1],
                "category": article[2],
                "source": article[3],
                "title": article[4],
                "author": article[5],
                "url": article[6],
                "body": article[7],
                "imageUrl": article[8],
                "readTime": article[9],
            }
        )

    return cleaned_articles


# Clean the articles returned by GoogleNews
def clean_articles(articles):
    # Add limiter to the number of articles returned
    limiter = 6
    articles = articles[:limiter]

    # Print first article
    logging.info("First article: %s", articles[0])

    # Add "body" key to each news article object
    for article in articles:
        try:
            # Get the final URL for the article
            final_url = requests.get("http://" + article["link"]).url

            # Parse the article using newspaper3k
            logging.info("Parsing article %s", final_url)
            news_article = Article(final_url)
            news_article.download()
            news_article.parse()

            # Add the "body" key to the article object
            article["body"] = news_article.text
            # Add the "image" key to the article object
            article["image"] = news_article.top_image
            # Add the "authors" key to the article object
            article["authors"] = news_article.authors
            # Reformat the "datetime" key to Mmm DD, YYYY and store to "date"
            article["date"] = article["datetime"].strftime("%b %d, %Y")
            # Add the "source" key to the article object
            article["source"] = article["media"]
            # Add the "read_time" key to the article object
            article["read_time"] = str(readtime.of_text(news_article.text))

            # Remove unnecessary keys
            del article["datetime"]
            del article["desc"]
            del article["img"]
            del article["link"]
            del article["media"]
            del article["site"]

        except Exception as e:
            logging.error("Error parsing article: %s", str(e))
            continue

    return articles


# Define a GET method for "demo" endpoint
@flask_app.route("/demo", methods=["GET"])
def demo():
    # Try-except block to handle errors
    try:
        # Start counting time
        start = datetime.now()

        # Create "news" table with the following columns
        # id as primary key, url,  body, image
        if not table_exists(conn, "news"):
            run_query(
                conn,
                "CREATE TABLE news (id INTEGER PRIMARY KEY, url TEXT, body TEXT, image TEXT)",
            )

        # Get top headlines from NewsAPI
        url = "https://newsapi.org/v2/top-headlines?country=ph&apiKey=13328281630540aaa6c2750b76b5ee12"
        top_headlines = requests.get(url).json()

        # Count the number of articles
        logging.info("Number of articles: %d", len(top_headlines["articles"]))

        # For each article, parse the article using newspaper3k and append to data
        data = []
        for article in top_headlines["articles"]:
            # Get the final URL for the article
            final_url = requests.get(article["url"]).url

            # Parse the article using newspaper3k
            logging.info("Parsing article %s", final_url)
            try:
                news_article = Article(final_url)
                news_article.download()
                news_article.parse()

                # Append the article to the data list
                logging.info("Appending article %s", final_url)
                data.append(
                    (
                        final_url,
                        news_article.text,
                        news_article.top_image,
                    )
                )
            except Exception as e:
                logging.error("Error parsing article: %s", str(e))
                continue

        # Insert the data into the database
        logging.info("Inserting data into database")
        conn.cursor().executemany(
            "INSERT INTO news (url, body, image) VALUES (?, ?, ?)", data
        )
        conn.commit()

        # Return OK status with time elapsed
        return jsonify(
            {
                "status": "ok",
                "time": str(datetime.now() - start),
                "totalResults": len(data),
            }
        )

    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "demoreset" endpoint
@flask_app.route("/demoreset", methods=["GET"])
def demoreset():
    # Try-except block to handle errors
    try:
        # Drop the "news" table
        logging.info("Dropping table")
        run_query(conn, "DROP TABLE news")

        # Return OK status
        return jsonify({"status": "ok"})
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "parse" endpoint
@flask_app.route("/parse", methods=["GET"])
def parse():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        url = request.args.get("url")

        # Find url in database
        logging.info("Finding article %s", url)
        result = conn.execute(
            f"SELECT (body, image) FROM news WHERE url='{url}'"
        ).fetchone()

        if result is None:
            # Parse the article using newspaper3k
            logging.info("Parsing article %s", url)
            news_article = Article(url)
            news_article.download()
            news_article.parse()

            # Return the article body, image as a JSON response
            return jsonify(
                {
                    "body": news_article.text,
                    "image": news_article.top_image,
                }
            )

        # Return the article body, image as a JSON response
        return jsonify(
            {
                # "body": news_article.text,
                # "image": news_article.top_image,
                "body": result[0] if result[0] is not None else "",
                "image": result[1] if result[1] is not None else "",
            }
        )
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "date" endpoint
@flask_app.route("/date", methods=["GET"])
def date():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        date = request.args.get("date")

        # Get the top headlines from NewsAPI
        logging.info("Getting top headlines for %s", date)
        top_headlines = newsapi.get_top_headlines(
            country="us", language="en", page_size=100
        )
        result = top_headlines["articles"]

        # Filter the results by date
        result = [
            article for article in result if article["publishedAt"].startswith(date)
        ]

        # Return the results as a JSON response
        return jsonify(result)
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Define a GET method for "status" endpoint
@flask_app.route("/status", methods=["GET"])
def status():
    # Try-except block to handle errors
    try:
        # Show date and time, Python version, and memory usage
        logging.info("Getting system status")
        logging.info("Date and time: %s", datetime.now())
        logging.info("Python version: %s", sys.version)
        logging.info("Memory usage (app): %s", sys.getsizeof(flask_app))
        logging.info("Memory usage (conn): %s", sys.getsizeof(conn))
        logging.info("SQLite db path: %s", db_path())

        # Return as a JSON response
        return jsonify(
            {
                "date and time": str(datetime.now()),
                "python version": sys.version,
                "memory usage (app)": str(sys.getsizeof(flask_app)),
                "memory usage (conn)": str(sys.getsizeof(conn)),
                "sqlite db path": db_path(),
            }
        )
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500


# Run the app
if __name__ == "__main__":
    logging.info("Starting Flask app, listening on port %d", 8000)
    flask_app.run(host="0.0.0.0", port=8000)
