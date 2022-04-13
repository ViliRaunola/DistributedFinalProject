# DistributedFinalProject

This was done as a final assignment on LUT course called Distributed Systems

The main idea in this project was to implement a general search tree. The search tree is built by working threads. Once the article that is being searched is found, building the tree is stopped. After this we have the last leaf that is the article that we were looking for. Now we can backtrack the path through the tree thus giving us the links from start to finish. 

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
Mämmi is 3 clicks away from Death
```
