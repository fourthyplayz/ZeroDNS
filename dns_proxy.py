import socket
import threading
import os
from dnslib import DNSRecord, QTYPE, RR, A

# Enable ANSI escape codes in Windows CMD/PowerShell for colors
if os.name == 'nt':
    os.system('color')

def load_filters(filename="filters.txt"):
    try:
        with open(filename, "r") as f:
            # Read lines, strip whitespace, and ignore empty lines or comments
            return {line.strip().lower() for line in f if line.strip() and not line.startswith('#')}
    except FileNotFoundError:
        print(f"[-] {filename} not found. Starting without filters.")
        return set()

FILTERS = load_filters()

def get_domain(qname):
    # Remove trailing dot if present (e.g., 'example.com.' -> 'example.com')
    domain = str(qname)
    if domain.endswith('.'):
        domain = domain[:-1]
    return domain.lower()

def forward_request(data):
    """Forwards the raw DNS query to Cloudflare (1.1.1.1) and returns the response."""
    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    forward_socket.settimeout(5.0)
    try:
        forward_socket.sendto(data, ("1.1.1.1", 53))
        response, _ = forward_socket.recvfrom(8192)
        return response
    except socket.timeout:
        return None
    except Exception as e:
        return None
    finally:
        forward_socket.close()

def handle_client(data, addr, sock):
    try:
        # Parse the raw DNS request packet
        request = DNSRecord.parse(data)
        domain = get_domain(request.q.qname)
        
        # Check against our filter list
        if domain in FILTERS:
            print(f"\033[91m[BLOCK] {domain}\033[0m")
            # Create a DNS response answering with 0.0.0.0
            reply = request.reply()
            reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            sock.sendto(reply.pack(), addr)
        else:
            print(f"\033[92m[PASS] {domain}\033[0m")
            # Forward legitimate request to Cloudflare DNS
            response = forward_request(data)
            if response:
                sock.sendto(response, addr)
                
    except Exception as e:
        # General try-except to prevent weird packets from crashing the proxy
        # print(f"\033[93m[ERROR] Malformed packet from {addr}: {e}\033[0m")
        pass

def main():
    HOST = '127.0.0.1'
    PORT = 53
    
    print(f"[*] Loaded {len(FILTERS)} blocked domains from filters.txt")
    print(f"[*] Starting DNS proxy on {HOST}:{PORT}")
    
    # Set up UDP socket for DNS requests
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind((HOST, PORT))
    except PermissionError:
        print("\033[91m[ERROR] Permission denied. You might need to run as Administrator to bind to port 53.\033[0m")
        return
    except OSError as e:
        print(f"\033[91m[ERROR] Could not bind to port {PORT}. Is another DNS server running? ({e})\033[0m")
        return

    try:
        # Listen indefinitely
        while True:
            data, addr = server_socket.recvfrom(8192)
            # Handle each request in its own thread so slow networking doesn't block the proxy
            t = threading.Thread(target=handle_client, args=(data, addr, server_socket))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down DNS proxy...")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
