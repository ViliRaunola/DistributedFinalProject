from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import wikipediaapi #Source for using this library: https://pypi.org/project/Wikipedia-API/
import json




hostname = 'localhost'
portnumber = 3000

#The Class and run_server function is heavily inspired by these threads: https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1 
# https://stackoverflow.com/questions/5033222/is-simplexmlrpcserver-single-threaded

#This class enables this server to handle each request on their own threads
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

#function for testing the functionality of the server
def test():
    print('Hello from test function')
    return True

def check_articles(start_article, end_article):
    #Initializing wikipedia object and defining the language for the search
    wiki_wiki = wikipediaapi.Wikipedia('en') 
    
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


def run_server(host=hostname, port=portnumber):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr)
    
    server.register_function(test, 'test')
    server.register_function(check_articles, 'check_articles')

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