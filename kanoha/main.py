#!/usr/bin/env python3

import asyncio
from sqlitedict import SqliteDict
from network import KanohaProtocol
from commandhandler import CommandHandler
from auction import AppLogic
from timer import Timer 

timer = Timer()

def protocol_factory():
    global timer
    return KanohaProtocol(CommandHandler(AppLogic(timer)))

loop = asyncio.get_event_loop()
asyncio.ensure_future(timer.time())

# Each client connection will create a new protocol instance
coro = loop.create_server(protocol_factory, '0.0.0.0', 2505)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever();
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

