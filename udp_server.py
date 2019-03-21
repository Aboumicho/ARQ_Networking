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
            if(pq.size > 0 ):
                    print("*************\nGetting ready to reconstruct {} packets \n\n***********".format(pq.size))
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
        if(p.packet_type == 5):
              n = int(p.payload.decode("utf-8"))
              pq.setSize(n)  

        if(p.packet_type == 0 ):
                message.append(p.payload.decode("utf-8"))
                pq.add(p)
                #dir_path = os.path.dirname(os.path.realpath(__file__))
                #filename = request[1]

                #print(dir_path + "/" + filename)
                #print(os.path.isfile(dir_path + "/" + filename))
                print("------ DATA RECEIVED ---------")
                print("Router: ", sender)
                print("Packet: ", p)
                print("Payload: ", p.payload.decode("utf-8"))
                conn.sendto(p.to_bytes(), sender)
                print("-------- END DATAGRAM ---------\n\n")

    except Exception as e:
           print("Error: ", e)

        

def readFile(filePath):
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
