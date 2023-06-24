from settings import *
import requests
from requests.exceptions import RequestException
import pandas as pd
from storage import DBStorage
from urllib.parse import quote_plus
from datetime import datetime

def search_api(query, pages=int(RESULT_COUNT/10)):
    results = []

    for i in range(0, pages):
        # First rank of record on each page
        start = i * 10 + i
        url = SEARCH_URL.format(
            key=SEARCH_KEY,
            cx=SEARCH_ID,
            # Quotes our special characters to be encoded properly for url
            query=quote_plus(query),
            start=start
        )
        response = requests.get(url)
        data = response.json()

        results += data['items']

    results_dataframe = pd.DataFrame.from_dict(results)
    results_dataframe['rank'] = list(range(1, results_dataframe.shape[0] + 1))
    results_dataframe = results_dataframe[['link', 'rank', 'snippet', 'title']]
    
    return results_dataframe

def scrape_page(links):
    html = []

    for link in links:
        try:
            data = requests.get(link, timeout=5)
            html.append(data.text)

        except RequestException:
            html.append("")

    return html

def search(query):
    columns = ['query', 'rank', 'link', 'title', 'snippet', 'html', 'created']
    storage = DBStorage()

    stored_results = storage.query_results(query)

    if stored_results.shape[0] > 0:
        stored_results['created'] = pd.to_datetime(stored_results['created'])
        return stored_results[columns]
    
    results = search_api(query)
    results['html'] = scrape_page(results['link'])
    results = results[results['html'].str.len() > 0].copy()

    results['query'] = query
    results['created'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    results = results[columns]
    results.apply(lambda x: storage.insert_row(x), axis=1)

    return results