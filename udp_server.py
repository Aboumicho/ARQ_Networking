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
        timeout = 30
        conn.settimeout(timeout)
        conn.bind(('', port))
        print('Echo server is listening at', port )
        print("\n")
        message = Message()
        pq = Queue()
        while True:
            data, sender = conn.recvfrom(1024)
            handle_client(conn, data, sender, message, pq)
    except socket.timeout: print('No response after {}s'.format(timeout)) 



def handle_client(conn, data, sender, message, pq):
    try:
        p = Packet.from_bytes(data)
        while(ack(conn, data, sender) == False):
                break
        response_server(conn, data, sender, message, pq, p)

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
    
def response_server(conn, data, sender, message, pq, p):

    try:
        p = Packet.from_bytes(data)
        """
        When all packets from a request were finally delivered

        """

        if(p.packet_type == 5):
              n = int(p.payload.decode("utf-8"))
              pq.setSize(n) 
              #print(message.message)
              request_handled = map_request(message.message, conn, sender, pq, p)
              x = 0
              if(message.message.split(" ")[0].lower() == "get".lower()):
                for packet in request_handled:                  
                                try:
                                        if(x==0):
                                                conn.settimeout(15)
                                        packet.peer_ip_addr = p.peer_ip_addr
                                        packet.peer_port = p.peer_port
                                        print("\n\n-------------SENDING RESPONSE TO CLIENT----------------")
                                        print(packet)
                                        print("---------------------RESPONSE--------------------------------\n\n")
                                        conn.sendto(packet.to_bytes(), sender)
                                        x += 1
                                except Exception as e: print('Error Packet #5: ', e)              
              print("Request: " + message.message.split(" ")[0].lower() + " Received")
              pq.reset()
              message.reset()
        if(p.packet_type == 0 ):
                if(pq.Size() == 0):
                        message.append(p.payload.decode("utf-8"))
                        pq.add(p)
                        print("------ PACKET RECEIVED ---------")
                        print("Router: ", sender)
                        print("Packet: ", p)
                        print("Payload: ", p.payload.decode("utf-8"))
                        conn.sendto(p.to_bytes(), sender)
                        print("-------- END PACKET ---------\n\n")
                elif(pq.list[-1].seq_num + 1 == p.seq_num): #If Previous packet received was the good one
                        message.append(p.payload.decode("utf-8"))
                        pq.add(p)
                        print("------ PACKET RECEIVED ---------")
                        print("Router: ", sender)
                        print("Packet: ", p)
                        print("Payload: ", p.payload.decode("utf-8"))
                        conn.sendto(p.to_bytes(), sender)
                        print("-------- END PACKET ---------\n\n")
                else:
                        print("previous packet not received")
    except Exception as e:
           print("Error: ", e)
"""
Response divided into 4-bytes packets

Returns list of packets
"""
def map_request(message, conn, sender, pq, p):
    m = message.split(" ")
    if(m[0].lower() == "GET".lower()):
            return get(message, conn, sender, pq, p)
    elif(m[0].lower() == "POST".lower()):
            return post(message, conn, sender, pq, p)

def post(message, conn, sender, pq, p):
    directory = os.path.dirname(os.path.realpath(__file__))   
    try:
        filename = message.split(" ")[1]
        writeFile(str(directory + "\\" + filename), filename, "POST")
        packet_queue = []
        return packet_queue
    except Exception as e:
        print("Error: " + e)   

def get(message, conn, sender, pq, p):
    directory = os.path.dirname(os.path.realpath(__file__))    
    file_content = ""
    packet_queue = []
    try:
        filename = message.split(" ")[1]
        file_content = str(readFile(directory + "\\" + filename))
        #Returns list of packets
        packet_queue = decompose_data(file_content, sender, pq, p)
        """
        i = 0
        while(i < len(packet_queue)):
                print(packet_queue[i])
                i += 1
        """
        return packet_queue
    except Exception as e:
        print("Error: " + e)

"""
Decomposes message into 4-bytes payload packets

returns a queue of packets

"""
def decompose_data(msg, sender, pq, p):
    message = list(msg)
    x = 0
    queue_size = 0
    peer_port = p.peer_port
    addr = p.peer_ip_addr  
    packet_queue = []
    m = ""
    syn_number = 0
    while(x < len(message)):
        m += message[x]
        if(x % 4 == 0):
            #create Packet with payload of 4-bytes 
            p = Packet(packet_type=0,
                seq_num=syn_number,
                peer_ip_addr=addr,
                peer_port=peer_port,
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
                peer_ip_addr=addr,
                peer_port=peer_port,
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
                peer_ip_addr=addr,
                peer_port=peer_port,
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

def writeFile(filePath, file_name, method):
        print(filePath)
        my_file = ""
        try:
                body =('\r\nHTTP/1.1 200 OK\r\n', # response line
                'Server: Crude Server\r\n', # header
                'Headers: {\r\n Content-Type: text/html\r\n}\r\n', # header
                'file: ' + str(file_name) + "\r\n",
                'method: ' + method + "\r\n",   
                "<html>\r\n <body>\r\n  <h1>Request received!</h1>\r\n </body>\r\n</html>\r\n") # response body
                my_file = open(filePath, "w")
                request = "".join(body)
                my_file.write(request)         
        except: print("ERROR OPENING FILE")
        finally: my_file.close()

# Usage python udp_server.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
args = parser.parse_args()
run_server(args.port)
