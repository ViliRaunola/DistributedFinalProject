import xmlrpc.client
import json
import time

#!TODO ADD COMMENTS

hostname = 'localhost'
portnumber = 3000

#Connecting to the server
rpc = xmlrpc.client.ServerProxy(f'http://{hostname}:{portnumber}')

def menu():
    print('\n-------------- Menu --------------')
    print('Select the next command')
    print('0. Quit the program')
    print('1. Get the shortest path between two Wikipedia articles')
    user_input = input('>>: ')
    return user_input

#Function that starts the search by confirming that the articles exists by calling the function check_articles on server
#Returns true to indicate that the execution can continue aka both articles exists
def start_search():
    start_article = input('Give the article name where to start the search: ')
    end_article = input('Give the article name to where to end the search: ')
    print('Checking if both articles exists before starting the search... Please Stand by!')
    response_for_article_check = rpc.check_articles(start_article, end_article)
    json_response = json.loads(response_for_article_check)

    if json_response['success']:
        print(json_response['message'])
    else:
        print(json_response['message'])
        print('Please try different articles!')
        return False

    print('Starting the search!')
    print('Searching....')
    start = time.time()
    response_for_path_search = rpc.shortest_path(start_article, end_article)
    json_response = json.loads(response_for_path_search)

    if json_response['success']:
        print(f'Path found! Search took {time.time()-start}s') #Source for using time: https://stackoverflow.com/questions/3144898/python-question-about-time-spent
        path = json_response['path']
        path.reverse()
        #print(json_response)
        i = 0
        for link in path:
            print(f'{link} ', end='')
            i = i + 1
            if i < len(path):
                print('-> ', end='')
    else:
        print(json_response['message'])
        return False


    return True

    
    


def main():

    try:
        while True:
            user_input = menu()
            if user_input == '1':
                if not start_search():
                    continue
            elif user_input == '0':
                print('Closing...')
                exit(0)
            else:
                print(f'"{user_input}" command is not supported, please try again!')
    
    except KeyboardInterrupt:
        print('Closing...')
        exit(0)
    except Exception as e:
        print(e)

main()