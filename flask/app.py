import sys
from flask import Flask, request, jsonify
from newspaper import Article
from GoogleNews import GoogleNews
import logging

# Configure the logging level and format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

# Configure the GoogleNews client
googlenews = GoogleNews(lang='en')

# Initialize the Flask application
flask_app = Flask(__name__)

# Error handler for incorrect URL
@flask_app.errorhandler(ValueError)
def value_error_handler(e):
    logging.error(e)
    return jsonify(error=str(e)), 404

# Define a GET method for "feed" endpoint
@flask_app.route('/feed', methods=['GET'])
def feed():
    # Try-except block to handle errors
    try:
        # Get feed from Google News
        googlenews.get_news('recent news')

        # Store results
        results = clean_articles(googlenews.results())

        # Clear GoogleNews results 
        googlenews.clear()

        # Return the feed as a JSON response
        return jsonify(results)

    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500
    

# Define a GET method for "search" endpoint
@flask_app.route('/search', methods=['GET'])
def search():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        query = request.args.get('q')
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
    
# Clean the articles returned by GoogleNews
def clean_articles(articles):
    # Add "body" key to each news article object
    for article in articles:
        # Parse the article using newspaper3k
        logging.info("Parsing article %s", article['link'])
        news_article = Article(article['link'])
        news_article.download()
        news_article.parse()

        # Add the "body" key to the article object
        article['body'] = news_article.text
    
    return articles

# Define a GET method for "parse" endpoint
@flask_app.route('/parse', methods=['GET'])
def parse():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        url = request.args.get('url')

        # Parse the article using newspaper3k
        logging.info("Parsing article %s", url)
        news_article = Article(url)
        news_article.download()
        news_article.parse()

        # Return the article as a JSON response
        return jsonify(news_article.text)
    except Exception as e:
        logging.error(e)
        return jsonify(error=str(e)), 500

# Run the app
if __name__ == '__main__':
    logging.info("Starting Flask app, listening on port %d", 8000)
    flask_app.run(host='0.0.0.0', port=8000)