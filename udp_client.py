import argparse
import ipaddress
import socket
import secrets
from packet import Packet
from urllib.parse import urlparse
import urllib.request
import os
import queue
from Message import Message

"""
Utf-8 uses 1 byte to encode each char 
Assuming all chars are in the range of the 128 US-ASCII characters. 
each Packet sent has to have payload = 4 bytes, which is 4 chars

"""

def run_client(router_addr, router_port, server_addr, server_port, args):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        #Syncronize
        syn(router_addr, router_port, server_addr, server_port)
        
        #Data Handling
        message = map_request(args)
        packet_list = decompose_data(message, args)
        q = ""
        request = Message()
        for packet in packet_list:  
            print(packet)          
            q = server_request(args, packet)

        
        #Reopening the socket
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind((router_addr,router_port))
        #conn.sendto(q.to_bytes(), (router_addr, router_port))
        packet_type = 0
        #request.append(q.payload.decode("utf-8"))
        while(packet_type != 5):
            response = conn.recv(1024)
            p = Packet.from_bytes(response) 
            packet_type = p.packet_type
            if(packet_type != 5):
                request.append(p.payload.decode("utf-8"))
            #conn.sendto(p.to_bytes(), (router_addr, router_port))
            print(p)
        print(request.message)
        conn.close()
        request.reset()       
        #print(p)
        #handle_server_request(router_addr, router_port, server_addr, server_port, args)    
    except Exception as e:
        print('Error: ', e)


"""

Method sends first SYN message to Server
Creates a Packet of Packet Type = 1
Sends a random Sequence Number to Server

"""
def syn(router_addr, router_port, server_addr, server_port):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 15
    msg = "Hi S"
    
    try:
        #Generate random sequence number for handshake
        syn_number = secrets.randbelow(1000)
        p = Packet(packet_type=1,
                   seq_num=syn_number,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print('Send "{}" to router'.format(msg))
        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print("\n\n-------STARTING HANDSHAKE, sending SYN --------")
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        print("------Server Response-----------")
        p = Packet.from_bytes(response)
        print("You sent " + str(p.seq_num-1) )
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))
        print("----------------------------- \n")

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        """
            *********
            Loops until Handshake is completed
            Ack() returns True when Packet TYPE = 3 

            *********
        """
        while(ack(router_addr, router_port, server_addr, server_port, p) == False ):
            print()
        conn.close()

def ack(router_addr, router_port, server_addr, server_port, p):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
    
    try:
        """
        If an ACK Packet Type was received
        Send a SYN-ACK to server
        By Incrementing Sequence number
        And making Packet Type 3
        """

        if(p.packet_type == 2):
            """
            FIRST PACKET 
            CONTAINING
            ACK: X + 1
            """
            timeout=15
            conn.settimeout(timeout)
            print("\n ------Sending Ack to Server-----------")
            print("You received y = " + str(p.seq_num) + ", Acknowledging sequence number by incrementing. y + 1: " + str(p.seq_num + 1) )
            p.seq_num = secrets.randbelow(1000)
            p.packet_type = 3
            print('Packet: ', p)
            print('Payload: ' + p.payload.decode("utf-8"))
            print("----------------------------- \n")
            conn.sendto(p.to_bytes(), (router_addr, router_port))

            
            
            return False
        """
        
        If a SYN-ACK Packet Type
        Print to client that connection was established

        """
        if(p.packet_type == 3):
            print("-------SYN-ACK completed, CONNECTION ESTABLISHED ------")
            print("Received sequence number: " +  str(p.seq_num))
            #p.payload = "ACK" 
            print("Packet: ", p) 
            print("--------End SYN-ACK MSG---------\n\n")
            return True

    except socket.timeout:
        print('No response after {}s'.format(timeout))
        return False
    return False
"""
Creates a list of Packets
Each Packet is of size 4 bytes
takes msg, which is the intended payload
takes args from command line

returns list of Packets
"""
def decompose_data(msg, args):
    message = list(msg)
    x = 0
    queue_size = 0
    
    packet_queue = []
    m = ""
    syn_number = 0
    peer_ip = ipaddress.ip_address(socket.gethostbyname(args.serverhost))
    while(x < len(message)):
        m += message[x]
        if(x % 4 == 0):
            #create Packet with payload of 4-bytes 
            p = Packet(packet_type=0,
                seq_num=syn_number,
                peer_ip_addr=peer_ip,
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
                peer_ip_addr=peer_ip,
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
                peer_ip_addr=peer_ip,
                peer_port=args.serverport,
                payload=str(queue_size).encode("utf-8"))
    )
    return packet_queue

def server_request(args, p):
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 30
    try:
        print("\n\n-------Sending data packets to server ------------")
                   
        conn.sendto(p.to_bytes(), (args.routerhost, args.routerport))
        
        print('Send {} to router'.format(p))
        print("--------------------------------------------------- \n\n")

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('\n\nWaiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        print("\n\n---------Received from server -------")
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))
        print("-----------------------------------------\n\n")
        print("----------DONE SENDING ----------")
        return p
    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close() 

def get_server(args):
	message = 'GET /' + args.url + ' HTTP/1.1'
	return message

def post_server(args):
    print(args)
    message = "POST " + args.url + " HTTP/1.1 " + "Host:"+ args.serverhost + " " + "User-Agent: Concordia-HTTP/1.0 "
    return message
	
def map_request(args):
    message = ""
    if args.command == "get":
        message = get_server(args)
    if args.command == "post":
        message = post_server(args)
    return message	

# Usage:
# python echoclient.py --routerhost localhost --routerport 3000 --serverhost localhost --serverport 8007

parser = argparse.ArgumentParser()
parser.add_argument("--routerhost", help="router host", default="localhost")
parser.add_argument("--routerport", help="router port", type=int, default=3000)
parser.add_argument("--serverhost", help="server host", default="localhost")
parser.add_argument("--serverport", help="server port", type=int, default=8007)
# Get/Post
parser.add_argument('command', choices=['get','post', 'help'], help="Executes a HTTP GET/POST request and prints the response.")
# Url
parser.add_argument('url', type=str, action="store", help="Url HTTP request is sent to")

args = parser.parse_args()

run_client(args.routerhost, args.routerport, args.serverhost, args.serverport, args)
