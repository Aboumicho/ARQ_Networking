import argparse
import socket
import os
from packet import Packet
import secrets
from ServerResponse import ServerResponse 
from Message import Message
from Queue import Queue

def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        print('Echo server is listening at', port )
        print("\n")
        message = Message()
        pq = Queue()
        while True:
            data, sender = conn.recvfrom(1024)
            handle_client(conn, data, sender, message, pq)

    finally:
        conn.close()


def handle_client(conn, data, sender, message, pq):
    try:
        p = Packet.from_bytes(data)
        while(ack(conn, data, sender) == False):
                break
        response_server(conn, data, sender, message, pq)

    except Exception as e:
        print("Error: ", e)

def ack(conn, data, sender):

    p = Packet.from_bytes(data)
    if(p.packet_type == 1):
        print("-------ACK from Server ------")
        print("Acknowledging x = " +  str(p.seq_num) + " by incrementing it. x + 1 =  "+str(p.seq_num + 1))
        p.seq_num = secrets.randbelow(1000)
        print("Sending new random value. y = " + str(p.seq_num))
        print("Received {} from Client. Sending Ack now.".format(p.payload.decode("utf-8")))
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p)  
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")
        return False
    if(p.packet_type == 2):
        print("-------Received ACK from Client ------")
        print("Received sequence number: " +  str(p.seq_num) + ". Now informing Client. ")
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p) 
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")
        return False
    if(p.packet_type == 3):
        print("-------Received ACK from Client, CONNECTION ESTABLISHED ------")
        print("Received sequence number: " +  str(p.seq_num) + ". Now informing Client. ")
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p) 
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")
        return True
    return False
    
def response_server(conn, data, sender, message, pq):

    try:
        p = Packet.from_bytes(data)
        """
        When all packets from a request were finally delivered

        """
        if(p.packet_type == 5):
              n = int(p.payload.decode("utf-8"))
              pq.setSize(n) 
              print(pq)
              #print(message.message)
              map_request(message.message, conn, sender, p)
              message.message=""
              pq.reset()

        if(p.packet_type == 0 ):
                message.append(p.payload.decode("utf-8"))
                pq.add(p)
                print("------ PACKET RECEIVED ---------")
                print("Router: ", sender)
                print("Packet: ", p)
                print("Payload: ", p.payload.decode("utf-8"))
                conn.sendto(p.to_bytes(), sender)
                print("-------- END PACKET ---------\n\n")

    except Exception as e:
           print("Error: ", e)

def map_request(message, conn, sender, p):
    m = message.split(" ")
    if(m[0].lower() == "GET".lower()):
            get(message, conn, sender, p)
    elif(m[0].lower() == "POST".lower()):
            post(message, conn, sender, p)

def post(filename, conn, sender, p):
    directory = os.path.dirname(os.path.realpath(__file__))   
    try:
        file_content = readFile(directory + "\\" + filename)
    except:
        print("Error: ")   

def get(message, conn, sender, p):
    directory = os.path.dirname(os.path.realpath(__file__))    
    file_content = ""
    packet_queue = []
    try:
        filename = message.split(" ")[1]
        file_content = str(readFile(directory + "\\" + filename))
        print(file_content)
        #packet_queue = decompose_data(file_content, sender)
    except:
        print("Error reading file")

"""
Decomposes message into 4-bytes payload packets

returns a queue of packets

"""
def decompose_data(msg, sender):
    message = list(msg)
    x = 0
    queue_size = 0
    
    packet_queue = []
    m = ""
    syn_number = 0
    while(x < len(message)):
        m += message[x]
        if(x % 4 == 0):
            #create Packet with payload of 4-bytes 
            p = Packet(packet_type=0,
                seq_num=syn_number,
                peer_ip_addr=sender,
                peer_port=args.serverport,
                payload=m.encode("utf-8"))
            #Add to queue
            packet_queue.append(p)
            syn_number += 1
            queue_size +=1
            #reset message to ""
            m = ""
        elif (x == len(message) - 1):
            #create Packet with payload of 4-bytes 
            p = Packet(packet_type=0,
                seq_num=syn_number,
                peer_ip_addr=sender,
                peer_port=args.serverport,
                payload=m.encode("utf-8"))
            queue_size += 1
            #Add to queue
            packet_queue.append(p)
            syn_number += 1
            #reset message to ""
            m = ""
        x += 1
    packet_queue.append(
        Packet(packet_type=5,
                seq_num=syn_number,
                peer_ip_addr=sender,
                peer_port=args.serverport,
                payload=str(queue_size).encode("utf-8"))
    )
    return packet_queue       

def readFile(filePath):
        response_code = 0
        response_body = ""
        if os.path.exists(filePath):
                response_code = 200
                with open(filePath) as f: 
                        response_body = f.read()
        else:
                response_code = 404
                response_body = "<h1>404 Not Found</h1>"

        blank_line = "\r\n"

        return ServerResponse(response_code, response_body).send()



# Usage python udp_server.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
args = parser.parse_args()
run_server(args.port)
