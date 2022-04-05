import xmlrpc.client


hostname = 'localhost'
portnumber = 3000

#Connecting to the server
rpc = xmlrpc.client.ServerProxy(f'http://{hostname}:{portnumber}')

def menu():
    print('--------------Menu--------------')
    print('Select the next command')
    print('1. Get the shortest path between two Wikipedia articles')
    user_input = input('>>: ')
    return user_input


def main():

    try:
        while True:
            user_input = menu()
            if user_input == '1':
                start_article = input('Give the article name where to start the search: ')
                end_article = input('Give the article name to where to end the search: ')
                response_for_article_check = rpc.checkArticles(start_article, end_article)
                print(response_for_article_check)
    
    except KeyboardInterrupt:
        print('Closing...')
    except Exception as e:
        print(e)

main()