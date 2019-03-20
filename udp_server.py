import argparse
import socket
import os
from packet import Packet


def run_server(port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        conn.bind(('', port))
        print('Echo server is listening at', port )
        print("\n")
        while True:
            data, sender = conn.recvfrom(1024)
            handle_client(conn, data, sender)

    finally:
        conn.close()



def handle_client(conn, data, sender):
    try:
        p = Packet.from_bytes(data)
        ack(conn, data, sender)
        response_server(conn, data, sender)
        # How to send a reply.
        # The peer address of the packet p is the address of the client already.
        # We will send the same payload of p. Thus we can re-use either `data` or `p`.
        #conn.sendto(p.to_bytes(), sender)

    except Exception as e:
        print("Error: ", e)

def ack(conn, data, sender):

    p = Packet.from_bytes(data)
    if(p.packet_type == 1):
        print("-------ACK from Server ------")
        print("Received sequence number: " +  str(p.seq_num) + ". Now sending sequence number + 1: "+str(p.seq_num + 1))
        p.seq_num = p.seq_num + 1
        print("Received {} from Client. Sending Ack now.".format(p.payload))
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p)  
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")
    if(p.packet_type == 2):
        print("-------Received ACK from Client ------")
        print("Received sequence number: " +  str(p.seq_num) + ". Now informing Client. ")
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p) 
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")
    if(p.packet_type == 3):
        print("-------Received ACK from Client, CONNECTION ESTABLISHED ------")
        print("Received sequence number: " +  str(p.seq_num) + ". Now informing Client. ")
        #p.payload = "ACK" 
        p.packet_type = 2
        print("Router: ", sender)
        print("Packet: ", p) 
        conn.sendto(p.to_bytes(), sender)
        print("--------End ACK MSG---------\n\n")

    
def response_server(conn, data, sender):

    try:      
        p = Packet.from_bytes(data)
        if(p.packet_type == 0 ):
                request = p.payload.decode("utf-8").split(" ")
                dir_path = os.path.dirname(os.path.realpath(__file__))
                filename = request[1].strip("/localhost/")
                #If url provided is a directory
                #if (os.path.isdir(dir_path + "/" + filename)):
                print(dir_path + "/" + filename)
                print(request)
                print("------ DATA RECEIVED ---------")
                print("Router: ", sender)
                print("Packet: ", p)
                print("Payload: ", p.payload.decode("utf-8"))
                conn.sendto(p.to_bytes(), sender)
                print("-------- END DATAGRAM ---------\n\n")
    except Exception as e:
           print("Error: ", e)




# Usage python udp_server.py [--port port-number]
parser = argparse.ArgumentParser()
parser.add_argument("--port", help="echo server port", type=int, default=8007)
args = parser.parse_args()
run_server(args.port)
