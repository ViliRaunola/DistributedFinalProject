from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import wikipediaapi #Source for using this library: https://pypi.org/project/Wikipedia-API/
import json
import queue
import threading
from concurrent.futures import ThreadPoolExecutor  #https://www.youtube.com/watch?v=BagTTT7l1pU
import requests
import time

hostname = 'localhost'
portnumber = 3000
MAX_LEVELS = 6 #Number of levels limiting the search three depth
MAX_WORKERS = 30
stop_search = False
lock = threading.Lock()

#Initializing wikipedia object and defining the language for the search
wiki_wiki = wikipediaapi.Wikipedia('en') 

#The Class SimpleThreadedXMLRPCServer and run_server function is heavily inspired by these threads: https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1 
# https://stackoverflow.com/questions/5033222/is-simplexmlrpcserver-single-threaded

#This class enables this server to handle each request on their own threads
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


#Source for using search tree on Python: https://www.youtube.com/watch?v=4r_XR9fUPhQ
class Node:
    
    def __init__(self, article_header):
        self.article_header = article_header
        self.children = []
        self.parent = None
    
    
    
    def add_child(self, child):
        child.parent = self
        self.children.append(child)
    

#https://www.youtube.com/watch?v=ipTWq6_2AGk
def find_path(found):
    # queue = [root]
    path = []
    node = found.get(0)
    # while queue:
    #     node = queue.pop(0)
    #     if node.parent:
    #         pass
    #         # path.append(node.parent.article_header) if node.parent.article_header not in path else path  #Source for adding to list if not in list: https://stackoverflow.com/questions/17370984/appending-an-id-to-a-list-if-not-already-present-in-a-string
    #     if node.article_header == end_article:
    #         break
    #     #Making sure that children list is not empty
    #     if node.children:
    #         queue.extend(node.children)
    
    path.append(node.article_header)
    while node.parent:
        path.append(node.parent.article_header)
        node = node.parent


    return path

    
   


#function for testing the functionality of the server

def test(searchterm):
    pass


def check_article(searchterm):
    session = requests.Session()
    #Define parameter and url for the api
    url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": searchterm,
    }

    response = session.get(url=url, params=params)


    #Try catch for the exception when this type of tree is not returned meaning that there are no articles on that name
    try:
        data = response.json()
        if data['query']['search'][0]['title'] == searchterm:
            return True
        else:
            #Nothing found, returning empty
            return False
    except:
        return False
    


#function to check wether the end and start points exists.
def check_articles(start_article, end_article):

    # #Initializing wikipedia object and defining the language for the search
    # wiki_wiki = wikipediaapi.Wikipedia('en') 

    #wiki_wiki.page().exists() returns true if page exists
    #start_article_exists = wiki_wiki.page(start_article).exists()
    #end_article_exists = wiki_wiki.page(end_article).exists()

    start_article_exists = check_article(start_article)
    end_article_exists = check_article(end_article)



    #Going through the results and generating appropiate return message
    if start_article_exists and end_article_exists:
        return_message = {
            'success': True,
            'message': 'Both articles found!'
        }
    elif not start_article_exists:
        return_message = {
            'success': False,
            'message': 'Start article not found'
        }
    elif not end_article_exists:
        return_message = {
            'success': False,
            'message': 'End article not found'
        }

    return json.dumps(return_message)

#Function to retreive the links of a article
#Source: https://www.mediawiki.org/wiki/API:Links
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

    #Try catch if the api tries to slow us down
    try:
        response = session.get(url=url, params=params)
        data = response.json()
        PAGES = data["query"]["pages"]
        for k, v in PAGES.items():
            for l in v["links"]:
                links.append(l['title'])
                #print(l['title'])
        return links
    except:
        return []

#Adding the found articles to a parent node    
def add_links_to_tree(links, parent, end_article, q, found):
    global stop_search
    
    for title in links:
        #title_exists = wiki_wiki.page(title).exists()
        #title_exists = check_article(title)
        #if title_exists:
        
        child = Node(title)
        
        parent.add_child(child)
        
        q.put(child) #Adds the new child also to the queue
        #If one of the articles matches the end result a global flag is raised
        if title == end_article:
            found.put(child)
            stop_search = True
            break
    

def worker(end_article, q, found):
    print('THREAD STARTED')
    while not stop_search:
        try:
            article = q.get(0) #Always getting the child that has been waiting the longest FIFO
            links = get_links(article.article_header)
            
            #lock.acquire()
            add_links_to_tree(links, article, end_article, q, found)
            #lock.release()
        
        except queue.Empty:
            print('Queue is empty sleeping...')
            time.sleep(0.1) 
    print('THREAD STOPPED')
    


#Function that handels the builindg of the search tree
def handle_search(start_article, end_article):
    q = queue.Queue()
    found = queue.Queue()

    links = get_links(start_article)
    root = Node(start_article)

    #Adding the links from the start article to the tree
    #                x      (0)
    #              / | \
    #             y  z  c   (1)
    add_links_to_tree(links, root, end_article, q, found)

    threads = []

    for _ in range(MAX_WORKERS):
        thread = threading.Thread(target=worker, args=(end_article, q, found))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    path = find_path(found)

    return_message = {
        'success': True,
        'path': path,
    }

    print('path is: ')
    print(path)

    return json.dumps(return_message)




def run_server(host=hostname, port=portnumber):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)
    
    server.register_function(test, 'test')
    server.register_function(check_articles, 'check_articles')
    server.register_function(handle_search, 'shortest_path')

    print('Server started on own thread')
    print(f'Server is listening on host {host} port {port}')

    server.serve_forever()


def main():
    run_server()

try:
    main()
except KeyboardInterrupt as e:
    print(e)
    print('Closing the server...')
    exit(0)