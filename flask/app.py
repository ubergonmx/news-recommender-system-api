import sys
from flask import Flask, request, jsonify
from newspaper import Article
from GoogleNews import GoogleNews
import logging
import requests
import readtime

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
    # Add limiter to the number of articles returned
    limiter = 6
    articles = articles[:limiter]

    # Add "body" key to each news article object
    for article in articles:
        try:
            # Get the final URL for the article
            final_url = requests.get('http://' + article['link']).url

            # Parse the article using newspaper3k
            logging.info("Parsing article %s", final_url)
            news_article = Article(final_url)
            news_article.download()
            news_article.parse()

            # Add the "body" key to the article object
            article['body'] = news_article.text
            # Add the "image" key to the article object
            article['image'] = news_article.top_image
            # Add the "authors" key to the article object
            article['authors'] = news_article.authors
            # Reformat the "datetime" key to Mmm DD, YYYY and store to "date"
            article['date'] = article['datetime'].strftime("%b %d, %Y")
            # Add the "source" key to the article object
            article['source'] = article['media']        
            # Add the "read_time" key to the article object
            article['read_time'] = str(readtime.of_text(news_article.text))

            # Remove unnecessary keys
            del article['datetime']
            del article['desc']
            del article['img']
            del article['link']
            del article['media']
            del article['site']
            
        except Exception as e:
            logging.error("Error parsing article: %s", str(e))
            continue
    
    return articles

# Define a GET method for "parse" endpoint
@flask_app.route('/parse', methods=['GET'])
def parse():
    # Try-except block to handle errors
    try:
        # Get the query string from the query parameters
        url = request.args.get('url')

        # Get the final URL for the article
        final_url = requests.get('http://' + url).url

        # Parse the article using newspaper3k
        logging.info("Parsing article %s", final_url)
        news_article = Article(final_url)
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