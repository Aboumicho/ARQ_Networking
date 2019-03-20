import argparse
import ipaddress
import socket
import secrets
from packet import Packet
from urllib.parse import urlparse
import urllib.request
import os

def run_client(router_addr, router_port, server_addr, server_port):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        msg = "Hello World"
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=msg.encode("utf-8"))
        syn(router_addr, router_port, server_addr, server_port)
        conn.sendto(p.to_bytes(), (router_addr, router_port))
        print('Send "{}" to router'.format(msg))

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close()
"""

Method sends first SYN message to Server
Creates a Packet of Packet Type = 1
Sends a random Sequence Number to Server

"""
def syn(router_addr, router_port, server_addr, server_port):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        msg = "Hi Server"
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
        ack(router_addr, router_port, server_addr, server_port, p)
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
            timeout=5
            conn.settimeout(timeout)
            print("\n ------Sending Ack to Server-----------")
            print("You received " + str(p.seq_num) + ", Sending sequence number + 1: " + str(p.seq_num + 1) )
            p.seq_num = p.seq_num + 1
            p.packet_type = 3
            print('Packet: ', p)
            print('Payload: ' + p.payload.decode("utf-8"))
            print("----------------------------- \n")
            conn.sendto(p.to_bytes(), (router_addr, router_port))
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

    except socket.timeout:
        print('No response after {}s'.format(timeout))

def server_request(args, message):
    peer_ip = ipaddress.ip_address(socket.gethostbyname(args.serverhost))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5
    try:
        msg = message
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=args.serverport,
                   payload=msg.encode("utf-8"))
                   
        conn.sendto(p.to_bytes(), (args.routerhost, args.routerport))
        print('Send "{}" to router'.format(msg))

        # Try to receive a response within timeout
        conn.settimeout(timeout)
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Packet: ', p)
        print('Payload: ' + p.payload.decode("utf-8"))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close() 

def get_server(args):
	message = 'GET /' + args.url + ' HTTP/1.1'
	return message
    #if args.headers: 
	#	for i in range(len(args.headers)):
	#		message += args.headers[i] + "\r\n"
	#connect_server("localhost", message, args)

def post_server(args):
    print(args)
    message = "POST " + args.url + " HTTP/1.1 " + "Host :  "+ args.serverhost + " " + "User-Agent : Concordia-HTTP/1.0 \r\n"
    return message
	#connect_server("localhost", message, args)
	
def map_request(args):
    message = ""
    if args.command == "get":
        message = get_server(args)
    if args.command == "post":
        message = post_server(args)
    #Send request to server
    server_request(args, message)	

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

map_request(args)
run_client(args.routerhost, args.routerport, args.serverhost, args.serverport)
