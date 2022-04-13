# DistributedFinalProject

This was done as a final assignment on LUT course called Distributed Systems

The task was to build a distributed system that finds the shortest path between two Wikipedia articles. More detailed documentation in the repository as PDF-file.

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
Link for a YouTube-video that show the execution and general structure of the system:
```link
https://youtu.be/BWgY070F2Z8
```
