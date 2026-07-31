"""Force outbound HTTP over IPv4.

DNS for openrouter.ai returns IPv6 addresses first, but the IPv6 route to Cloudflare blackholes
on some networks. Python's socket layer tries each address in order and waits out the full TCP
timeout (~60s each) before falling back to IPv4, so every API call took minutes. curl avoids
this with Happy Eyeballs (parallel IPv4/IPv6); Python has no such thing.

Importing this module patches urllib3 to skip IPv6 entirely. Safe to import more than once.
"""

import socket

import urllib3.util.connection as urllib3_connection

urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
