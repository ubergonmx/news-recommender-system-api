# DEPRECATED
This project is no longer maintained; please consider using [https://github.com/ubergonmx/newsmead-api](https://github.com/ubergonmx/newsmead-api) instead.

-----

# NewsMead API

A news recommender API built with Flask/Python for the NewsMead mobile app.

## Tech Stack

- Python
- Flask
- Azure Services: Web App

## API Endpoints

API URL: https://newsmead.azurewebsites.net/

List of **GET** endpoints:

- `/feed` - returns articles scraped from Google News
- `/top` - returns top headline articles from News API
- `/search?q=[query]` - returns articles searched with the query and scraped from Google News
- `/parse?url=[url]` - returns scraped content of the article from the given url

## How to run

Note: Must have Python version 3.9 for recommenders package.

1. Install requirements

```bash
pip install -r requirements.txt
```

2. Go to `/flask` directory

```bash
cd flask
```

3. Run Flask

```bash
flask run
# or
python -m flask run
```
