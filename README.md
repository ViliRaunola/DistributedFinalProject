# DistributedFinalProject

This was done as a final assignment on LUT course called Distributed Systems

The main idea in this project was to implement a general search tree. The search tree is built by working threads. Once the article that is being searched is found, building the tree is stopped. After this we have the last leaf that is the article that we were looking for. Now we can backtrack the path through the tree thus giving us the links from start to finish. Building the tree is done one layer at a time.

The RPC server can handle multiple clients at once. You can start a longer search on one client and an other client can still make their own calls to the server and get response before the other one finishes.

To run the code:
  1. Start the server
 ```
 server.py
 ```
  2. Start the client
  ```
  client.py
  ```
    
Excpected output for example route between Mämmi and Death:
```console
Path found! Search took 4 s
Mämmi -> Birch bark -> Creosote -> Death
Death is 3 clicks away from Mämmi
```
