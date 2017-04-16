import requests
from xmltodict import parse
from json import dumps

if __name__ == "__main__":
    xml = requests.get("http://export.arxiv.org/api/query?search_query=all&max_results=1000").text
    with open("arxiv.json", "w") as f:
        f.write(dumps(parse(xml).get("feed").get("entry")))
