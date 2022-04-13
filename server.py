from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import json
import queue
import threading
import requests
import time

hostname = 'localhost'
portnumber = 3000
MAX_WORKERS = 20 #Number of threads that are created
MAX_DEPTH = 6 #Variable to check the depth of the search when to stop
STOP_SEARCH = False #Global flag that is used to control all of the working threads
MAX_DEPTH_FLAG = False #Global flag raised if the depth was reached
ALLOW_DEPTH_CHECK = True #Global flag to allow the depth check. Is cpu intensive so don't really want to be used
lock = threading.Lock()
lock3 = threading.Lock()


#The Class SimpleThreadedXMLRPCServer and run_server function is heavily inspired by these threads: 
# https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1 
# https://stackoverflow.com/questions/5033222/is-simplexmlrpcserver-single-threaded

#This class enables this server to handle each request on their own threads
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


#Source for using general search tree on Python: https://www.youtube.com/watch?v=4r_XR9fUPhQ
class Node:
    #The node
    def __init__(self, article_header):
        self.article_header = article_header #Article/ link name
        self.children = []  #All of the children nodes
        self.parent = None #Parent of this node
        self.depth = 0 #Node depth on the tree
    #Function to add children
    def add_child(self, child):
        child.parent = self #When calling as parent.add_child(child) self refers to parent --> aka childs parent comes the parent :D
        self.children.append(child) #Adding the child to the parent's children list
        child.depth = self.depth + 1 #Child's level is one more that the parents

    

#Uses the found child article to reverse the path
def find_path(found):
    path = [] #Stores the path from end to start
    node = found.get(0) #Getting the child node from the queue
    path.append(node.article_header) #Adding the child node name to the
    #Traversing back to the parent
    while node.parent:
        path.append(node.parent.article_header) #Adding the parent's name to the path
        node = node.parent

    return path

#Function to get the nodes depth in the tree
def get_depth(node):
    path = [] #Stores the path from end to start
    path.append(node.article_header) #Adding the child node name to the
    #Traversing back to the parent
    while node.parent:
        path.append(node.parent.article_header) #Adding the parent's name to the path
        node = node.parent

    depth = len(path)

    return depth



#Function to check if the article exists on wikipedia
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

    #Try catch for the exception when this type of tree is not returned meaning that there are no articles on that name
    try:
        response = session.get(url=url, params=params)
        data = response.json()
        if data['query']['search'][0]['title'] == searchterm:
            return True
        else:
            #Nothing found, returning empty
            return False
    except Exception as e:
        print(e)
        print('Error in searching the article')
        return False
    


#Function to check wether the end and start points exists.
def check_articles(start_article, end_article):
    #Is locked so only one client can use it once
    with lock3:

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


#SOURCE: https://www.mediawiki.org/wiki/API:Links
#Functions to get the remaining links from the API call
def get_links_more(url, params, session, links):
    
    while True:
        response = session.get(url=url, params=params)
        data = response.json()
        pages = data["query"]["pages"]
        for k, v in pages.items():
            for l in v["links"]:
                if(l["ns"] == 0):
                    links.append(l['title'])
        if 'continue' in data:
                if 'plcontinue' in data['continue']:
                    params['plcontinue'] = data['continue']['plcontinue']
        else:
            break
        

#Function to retreive the links of a article, is mainly copy pasted from wikipedia's documentation!
#SOURCE: https://www.mediawiki.org/wiki/API:Links
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
    #SOURCE: https://www.mediawiki.org/wiki/API:Links

    response = session.get(url=url, params=params)
    
    try:
        data = response.json()
        pages = data["query"]["pages"]

        for k, v in pages.items():
            for l in v["links"]:
                if(l["ns"] == 0): #Source for removing empty links https://stackoverflow.com/questions/40579942/what-do-the-parameters-in-wikipedia-api-response-mean
                    links.append(l['title'])
                    #print(l['title'])

        if 'continue' in data:
            if 'plcontinue' in data['continue']:
                continue_parameter = data['continue']['plcontinue']
                params['plcontinue'] = continue_parameter
                get_links_more(url, params, session, links)
                
        return links
    except KeyError as e:
        return ['--1']
    except json.decoder.JSONDecodeError as e: #Error when the Wikipedia API tries to block us
        return ['--1']

#Adding the found articles to a parent node    
def add_links_to_tree(links, parent, end_article, q, found):
    global STOP_SEARCH, MAX_DEPTH_FLAG
    
    #Check if the depth cheking is allwed or not
    if ALLOW_DEPTH_CHECK:
        if MAX_DEPTH < parent.depth:
            STOP_SEARCH = True
            MAX_DEPTH_FLAG = True

    
    for title in links:        
        child = Node(title) #Creating the node
        parent.add_child(child) #Adding the node to its parent
        
        q.put(child) #Adds the new child also to the queue
        #If one of the articles matches the end result a global flag is raised and threads all stopped
        #print(f'Depth is now: {child.depth}')
        if title == end_article:
            found.put(child) #Adding the child to the found queue where it is retreived for path analysis
            STOP_SEARCH = True #Raising the stop flag
            break
    
    

#The main worker thread
#Processes one child node at once. Gets all the links it has and adds the links as childs back to itself
def worker(end_article, q, found):
    #Will get a child node from the queue until a stop flag is raised indicating that the article is found
    while not STOP_SEARCH:
        try:
            article = q.get(0) #Always getting the child that has been waiting the longest FIFO
            links = get_links(article.article_header)
            if len(links) > 0:
                #If the Wikipedia API blocked us we didn't get any info from that child so it must be put back to the queue
                #This means that the breadth first search is compromised!!!!
                if links[0] == '--1': 
                    q.put(article)
                    continue
            
            add_links_to_tree(links, article, end_article, q, found)
            
        #Incase we empty the queue due to too many workers/ slow api resulting in no links
        except queue.Empty:
            print('Queue is empty sleeping...')
            time.sleep(0.1) 
    
    


#Function that handels the working threads
def handle_search(start_article, end_article):
    #Adding a lock for this fuction. Otherwise running this with another RPC thread would couse problems
    with lock:
        global STOP_SEARCH, MAX_DEPTH_FLAG
        links = [] #Array for links that is needed for creating the root node
        q = queue.Queue()   #Queue that keeps track of the child nodes that need to be processed next. Child nodes are added breadth first
        found = queue.Queue()   #Queue that will be used to transfer the child node that has the end article
        
        #Adding the links from the start article to the tree as a root
        #                x      (0)  <-- root
        #              / | \
        #             y  z  c   (1)
        links = get_links(start_article)
        root = Node(start_article)
        add_links_to_tree(links, root, end_article, q, found)

        threads = [] #Array that keeps track of the created threads

        #Creating a fixed amount of working threads
        #Source: https://stackoverflow.com/questions/55529319/how-to-create-multiple-threads-dynamically-in-python
        #Source for using _ in loop: https://stackoverflow.com/questions/66425508/what-is-the-meaning-of-for-in-range
        for _ in range(MAX_WORKERS):
            thread = threading.Thread(target=worker, args=(end_article, q, found))
            thread.start()
            threads.append(thread)
        print(f'All {MAX_WORKERS} threads started!')
        #Waiting for all of the threads to finish before continuing. Same source as creating threads
        for thread in threads:
            thread.join()
        print('All threads closed')


        #If the max_depth flag was raised
        if MAX_DEPTH_FLAG:
            #Clearing the queues when exiting the thread: https://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
            with q.mutex:
                q.queue.clear()
            
            with found.mutex:
                found.queue.clear()
        
            #Resetting the global flags
            STOP_SEARCH = False 
            MAX_DEPTH_FLAG = False

            return_message = {
                'success': False,
                'message': f'Maximum depth reached of {MAX_DEPTH}',
            }

            return json.dumps(return_message)

            

        #Getting the path between the articles
        path = find_path(found)

        return_message = {
            'success': True,
            'path': path,
        }

        #Clearing the queues when exiting the thread: https://stackoverflow.com/questions/6517953/clear-all-items-from-the-queue
        with q.mutex:
            q.queue.clear()
        
        with found.mutex:
            found.queue.clear()
        
        #Resetting the global flags
        STOP_SEARCH = False 
        MAX_DEPTH_FLAG = False

        return json.dumps(return_message)


#Sources for multithreded rpc server: https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1 
# https://stackoverflow.com/questions/5033222/is-simplexmlrpcserver-single-threaded


def run_server(host=hostname, port=portnumber):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)
    
    server.register_function(check_articles, 'check_articles')
    server.register_function(handle_search, 'shortest_path')

    print('Server started on own thread')
    print(f'Server is listening on host {host} port {port}')

    server.serve_forever()


def main():
    run_server()

#For closing the server
try:
    main()
except KeyboardInterrupt as e:
    print('Closing the server...')
    exit(0)