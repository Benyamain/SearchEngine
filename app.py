from flask import Flask, request
from search import search
import html

app = Flask(__name__)

search_template = """
<form action="/" method="post">
    <input type="text" name="query">
    <input type="submit" value="Search">
</form>
"""

result_template = """
<p class="site">{rank}: {link}</p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""

def show_search_form():
    return search_template

def run_search(query):
    results = search(query)
    rendered = search_template
    # Not render random html that exists within the snippet
    results['snippet'] = results['snippet'].apply(lambda x: html.escape(x))

    for index, row in results.iterrows():
        rendered += result_template.format(**row)

    return rendered

@app.route("/", methods=["GET", "POST"])
def search_form():
    if request.method == "POST":
        query = request.form['query']
        return run_search(query)
    
    else:
        return show_search_form()