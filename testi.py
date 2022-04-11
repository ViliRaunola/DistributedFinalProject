import requests

def get_links(parent_article):
    
    session = requests.Session()
    links = []
    #Define parameter and url for the api
    url = "https://en.wikipedia.org/w/api.php"
    
    params = {
    "action": "query",
    "format": "json",
    "titles": parent_article,
    "prop": "links",
    "pllimit": "max",
    }

    response = session.get(url=url, params=params)
    data = response.json()
    PAGES = data["query"]["pages"]
    try:
        for k, v in PAGES.items():
            for l in v["links"]:
                links.append(l['title'])
                #print(l['title'])
        return links
    except:
        return []

def main():
    links = get_links('Elizabeth II')
    for link in links:
        print(link)

main()