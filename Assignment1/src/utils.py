import socket
from urllib.parse import urlparse

def get_hostname_from_URL(URL: str):
     parsed = urlparse(URL)
     return parsed.hostname

def get_scheme_from_URL(URL: str):
     parsed = urlparse(URL)
     return parsed.scheme

def get_ip_from_URL(URL: str):
        HOST_NAME = get_hostname_from_URL(URL)
        try:
            server_IP = socket.gethostbyname(HOST_NAME)
        except Exception as e:
            print(f'get_ip_from_URL threw : {e}')
            server_IP = HOST_NAME
        return server_IP