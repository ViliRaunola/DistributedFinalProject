from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import wikipediaapi #Source for using this library: https://pypi.org/project/Wikipedia-API/
import json

hostname = 'localhost'
portnumber = 3000

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
        self.childern = []
        self.parent = None
    
    def add_child(self, child):
        child.parent = self
        self.childern.append(child)
        


#function for testing the functionality of the server
def test():
    print('Hello from test function')
    return True

#function to check wether the end and start points exists.
def check_articles(start_article, end_article):
    
    
    #wiki_wiki.page().exists() returns true if page exists
    start_article_exists = wiki_wiki.page(start_article).exists()
    end_article_exists = wiki_wiki.page(end_article).exists()


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
def get_links(parent_article):
    
    #Using the wikipediaapi to get the page
    page = wiki_wiki.page(parent_article)

    #from the page get all of the links
    links = page.links

    return links

#Adding the found articles to a parent node    
def add_links_to_tree(links, parent, end_article):
    for title in links.keys():
        title_exists = wiki_wiki.page(title).exists()
        if title_exists:
            child = Node(title)
            parent.add_child(child)
        #If one of the articles matches the end result a global flag is raised
        if title == end_article:
            stop_search = True
            break

#Function that handels the builindg of the search tree
def create_tree(start_article, end_article):
    links = get_links(start_article)
    
    root = Node(start_article)

    add_links_to_tree(links, root, end_article)

    # for title in links.keys():
    #     links2 = get_links(title)
        
    #     break
    

    return 0



def run_server(host=hostname, port=portnumber):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)
    
    server.register_function(test, 'test')
    server.register_function(check_articles, 'check_articles')
    server.register_function(create_tree, 'shortest_path')

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