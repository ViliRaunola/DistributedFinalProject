
import requests


def get_links_more(url, params, session):
    links = []

    while True:
        response = session.get(url=url, params=params)
        data = response.json()
        print(data)
        PAGES = data["query"]["pages"]
        
        for k, v in PAGES.items():
            for l in v["links"]:
                if(l["ns"] == 0):
                    links.append(l['title'])

        
        if 'continue' in data:
                if 'plcontinue' in data['continue']:
                    params['plcontinue'] = data['continue']['plcontinue']
        else:
            break
    return links



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
    print(data)
    pages = data["query"]["pages"]
    try:
        for k, v in pages.items():
            for l in v["links"]:
                if(l["ns"] == 0):
                    links.append(l['title'])
                #print(l['title'])
        if 'continue' in data:
            if 'plcontinue' in data['continue']:
                continue_parameter = data['continue']['plcontinue']
                params['plcontinue'] = continue_parameter
                links.extend(get_links_more(url, params, session))

        return links
    except KeyError:
        return []

def main():
    links = get_links('Jesus')
    for link in links:
        print(link)
    print(len(links))

main()