#!/usr/bin/python
import sys
import logging
import logging.config
import subprocess
from marionette import Marionette

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

flog = open("/tmp/m.log", "w")

logging.basicConfig()
logger = logging.getLogger('m_viewer')
logger.info('start marionette client')


def init():
    ret = subprocess.check_output("adb devices", shell=True)
#    if("unagi" in ret):
#        print(ret)
#    else:
#        print("No unagi connected")
#        sys.exit(1)
    import socket
    s = socket.socket()
    try:
        s.bind(("localhost", 2828))
        s.close()
        ret = subprocess.check_output("adb forward tcp:2828 tcp:2828", shell=True)
    except socket.error:
        print("address already in use")
    mar = Marionette()
    mar.start_session()
    return mar

## Start a marionette instance
m = init()


## Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

## Create server
server = SimpleXMLRPCServer(("localhost", 1337),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

server.register_instance(m)


# Register pow() function; this will use the value of
# pow.__name__ as the name, which is just 'pow'.
def get_page_source():
    return m.page_source
server.register_function(get_page_source)


def enter_frame(iframe=None):
    flog.write('write iframe = %s' % iframe)
    if iframe is None:
        m.switch_to_frame()
        return m.page_source
    fr = m.find_element("css selector", 'iframe[%s]' % iframe)
    logger.info('iframe[%s]' % iframe)
    m.switch_to_frame(fr)
    return m.page_source
server.register_function(enter_frame)

## Register an instance; all the methods of the instance are
## published as XML-RPC methods (in this case, just 'div').

## Run the server's main loop
server.serve_forever()

flog.close()
