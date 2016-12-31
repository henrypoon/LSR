from socket import socket, AF_INET, SOCK_DGRAM, timeout
from sys import*
import sched
import time
import threading 
import random
from heapq import*


localID = str(argv[1])
listen_addr = '127.0.0.1'
listen_port = int(argv[2])
configName = argv[3]
listen = (listen_addr, listen_port)
socket = socket(AF_INET, SOCK_DGRAM)
socket.bind(listen)
edges = {}
neighbourList = {}
forward  = set()
liveCount = {}
updataFlag = False
deleteID = []
record = {}


def initial(content):					#initial program, build up initial graph from the information given by config file
	global edges
	global neighbourList
	global neighbourNo	
	global localID
	global Flag
	edges[localID] = {}

	line = content.split("\n")	
	neighbourNo = line[0]
	line.pop(0)
	line.pop(-1)
	#print line
	for k in line:
		node = k.split (" ")
		ID = node[0]
		liveCount[ID] = 0
		cost = float(node[1])
		port = int(node[2])
		neighbourList[ID] = port;
	
		edges[ID] = {}							#add edges at the beginning
		edges[localID][ID] = cost
		edges[ID][localID] = cost




def readPacket(content):				#analysis the link-state packet via flooding
	global edges
	global record	

	lines = content.split('\n')
	

	for k in lines:
	
		tempList = edges.copy()												  
																					
		if "From" in k:											#can know which node send this packet initially			
			source = k.split(' ')											
																					
			ID = source[1]
			seq = source[2]

			if ID == localID:
				send = False
			else:	
				if record.has_key(ID) == False:
					record[ID] = seq
					send = True
				else:
					if seq < record[ID]:
						send = False
					else:
						record[ID] = seq
						send = True
		
		else:													#add edges
			if k != '':
				#print k
				info = k.split (" ")
				fromID = info[0]
				toID = info[1]
				cost = float(info[2])
				if fromID not in tempList:
					tempList[fromID] = {}

				if toID not in tempList:
					tempList[toID] = {}

				tempList[fromID][toID] = cost
				tempList[toID][fromID] = cost
				edges = tempList.copy()					

	return send



def dijsktra(dest):							#search by dijsktra algo
	q = []
	path = []
	visited = {}
	cost = {}
	previous ={}
	tempList = edges.copy()


	for node in tempList:

		visited[node] = False						#preset all nodes as unvisited
		cost[node] = float(100000000)
	cost[localID] = 0

	heappush(q,(0,localID))				#put this node into the queue

	while q:
		currNode = heappop(q)[1]				#pop out the smallest one
		#print curr
		visited[currNode] = True

		for node in tempList[currNode]:
			if visited[node] == False:
				total = cost[currNode] + tempList[currNode][node]

				if total< cost[node]:				#update if find smaller cost
						cost[node] = total
						previous[node] = currNode
				heappush(q,(total,node))
	temp = dest
	
	while temp != localID:					#store the shortest path
		path.insert(0, temp)
		temp = previous[temp]
	path.insert(0, localID)

	return (path, cost[dest])




def LSpacket():						#prepare the link-state packet
	global forward 
	forward = set()
	List = edges.copy()

	for j in List:
		for k in List[j]:
			info = str(j) + " "+str(k) + " "+ str(List[j][k])
			forward.add(info)



def receiver(content):

	received = set()
	deleteInfo = set()
																						#initial the counter for each neighbour
	counter = {}
	for k in neighbourList:						
		dic = threading.Timer(3, removeNode, args = (k,0,))
		dic.daemon = True
		dic.start()
		counter[k] = dic


	global socket
	#socket.settimeout(0.01)
	while True:
		try:
			message, address = socket.recvfrom(4096)
			#print message
			content = message										#receive the notification for deleting the dead node
			if " Delete" in content:


				if message not in deleteInfo:		
					#print message
					deleteInfo.add(message)
					tempList = neighbourList.copy()

					t = content.split(' ')

					deleteID = t[0]

					if deleteID in edges and deleteID not in neighbourList:

						removeNode(deleteID,1)
						tempList = neighbourList.copy()
						for k in tempList:
							if k != deleteID:
								dest = (listen_addr, int(tempList[k]))
								socket.sendto(content, dest)
				
			else:
	
				if "heartbeat" not in message:					#if receive the heart beat packet
					if message not in received:		
						received.add(message)
						tempList = neighbourList.copy()

						send = readPacket(message)
						if send == True:

							for node in tempList:
								#print node
								if (str(tempList[node]) != str(address[1])):
									dest = (listen_addr, int(tempList[node]))
									socket.sendto(message, dest)
				else:								# if receive the link-state packet

					temp = message.split(' ')
					thisID = temp[0]
					count = temp[1]
					counter[thisID].cancel()
					new = threading.Timer(3, removeNode, args = (thisID,0,))
					new.daemon = True
					new.start() 
					counter[thisID] = new

		except timeout:
			pass



def removeNode(ID,mode):				#remove the specific node from the graph and update information

	global neighbourList
	global edges

	tempNeighbour = neighbourList.copy()
	tempEdges = edges.copy()


	print "Lost " + str(ID)

	if mode == 0:							# mode = 0 : local node found the dead node and send the notifications to others									
		for k in tempNeighbour:
			if k != ID:
				data = str(ID) + " Delete"
	 			dest = (listen_addr,int(tempNeighbour[k]))
				#print data
				socket.sendto(data, dest)


	if ID in tempEdges:
		for node in tempEdges[ID]:
			del tempEdges[node][ID]


		del tempEdges[ID]
		if ID in tempNeighbour:
			del tempNeighbour[ID]
			del liveCount[ID]

		tempList = forward.copy()

		for k in tempList:
			if str(ID) in k:
				forward.remove(k)

	neighbourList.clear()
	neighbourList = tempNeighbour.copy()
	edges.clear()
	edges = tempEdges.copy()



def flooding(content):				#flooding
	counter = 0
	while True:
		if updataFlag == False:
		#LSpacket()
			global listen_addr
			global neighbourList
			global localID
			global socket
			tempList = neighbourList.copy()
			LSpacket()
			for node in tempList:
				dest = (listen_addr, int(tempList[node]))
				temp = "\n"
				data = "From " + str(localID) + " " + str(counter) + "\n" +temp.join(forward)
				socket.sendto(data, dest)
			counter += 1
			time.sleep(1)





def heartBeat():				#keep send teh heartbeat packet to detect the dead node
	counter = 0
	tempList = neighbourList.copy()
	while updataFlag == False:
		for node in tempList:
			dest = (listen_addr, int(tempList[node]))
			data = str(localID)+" "+str(counter)+ " heartbeat"
			socket.sendto(data, dest)
		#print data
		counter += 1
		time.sleep(0.3)



def findShortestPath():
	while True:
			
		time.sleep(30)
		#print edges
		tempList = edges.copy()
		print "\n------------------------------------------------------------------------"
		for node in tempList:
			if node != localID:
				(path, cost) = dijsktra(node)
				out = ''.join(path)
				print "least-cost path to node "+node+": "+out+" and the cost is " + str(cost)
		print "-------------------------------------------------------------------------\n"

if __name__ == "__main__":

	with open(configName) as Source:			#read config file
		config = Source.read();
	Source.close()

	initial(config)

	flooding = threading.Thread(target = flooding, args = (config,))				#create a thread for flooding
	flooding.daemon = True
	flooding.start()

	receiver = threading.Thread(target = receiver, args = (config,))				#create a thread for receiver
	receiver.daemon = True
	receiver.start()

	alive = threading.Thread(target = heartBeat)								#create a thread for hearbeat checking
	alive.daemon = True
	alive.start()


	find = threading.Thread(target = findShortestPath, args=())			#create a thread for finding the shortest path to specifi node from this node
	find.daemon = True
	find.start()


while True:
	pass
