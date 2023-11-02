# News Recommender System API

An NRS API built with Flask/Python for NewsMead mobile app.

## Tech Stack

- Python
- Flask
- Azure Services: Web App

## API Endpoints

**GET** method

- `/feed` - returns articles scraped from Google News
- `/top` - returns top headline articles from News API
- `/search?q=[query]` - returns articles searched with the query and scraped from Google News
- `/parse?url=[url]` - returns scraped content of the article from the given url

## How to run

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
