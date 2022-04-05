import xmlrpc.client


hostname = 'localhost'
portnumber = 3000

#Connecting to the server
rpc = xmlrpc.client.ServerProxy(f'http://{hostname}:{portnumber}')


if rpc.test():
    print('rpc request returned true')
else:
    print('rpc request returned false')