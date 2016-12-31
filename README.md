This program can simulate broadcasting mechanism of router basing on UDP. Each node will broadcast a link state packet every second.
On receiving link-state packets from all other nodes, a router can build up a global view of the
network topology, a router will run Dijkstra's algorithm to compute least-cost paths to all other routers within the network. 
Each node should wait for 30 seconds since start-up and then execute
Dijkstra’s algorithm. 

Once a router finishes running Dijkstra’s algorithm, it will print out to the terminal, the leastcost
path to each destination node (excluding itself) along with the cost of this path.
The following is an example output for node A in some arbitrary network:
    least-cost path to node B: ACB and the cost is 10
    least-cost path to node C: AC and the cost is 2.5
    
The program also implement the feature of detecting failure of nodes. For detecting the dead node, the program would keep sending heart-beat packet to their neighbour nodes every 0.3 second. 
And if the program haven’t received any heart-beat packet from the same neighbour nodes for 3 second, that neighbour node would be counted as dead. 
Then it will delete that node in the graph and relative edges, also broadcast a notification to other nodes. 
And once the other nodes receive this notification, they will update their graph and prepare the new link-state packet. 
Since finding the least cost path is basing on the graph, the least cost path to others node would update afterwards.


The program basically uses two conditions to restrict the excessive like-state broadcasts: 
1. Stop broadcasting when received a linked-state packets that sent from itself  
2. Each received packet would be stored into a set without duplicate. And it would stop broadcasting that packet when observer that packet has been stored already.  


How to run:
The program will accept the following command line arguments:
  • NODE_ID, the ID for this node. This argument must be a single uppercase alphabet (e.g., A,
  B, etc).
  • NODE_PORT, the port number on which this node will send and receive packets to and from
  its neighbours.
  Updates to the assignment, including any corrections and clarifications, will be posted on the
  subject website. Please make sure that you check the subject website regularly for updates.
  • CONFIG.TXT, this file will contain the costs to the neighbouring nodes. It will also contain
  the port number being used by each neighbour for exchanging routing packets. An example of
  this file is provided below.
