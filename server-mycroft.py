#!/usr/bin/env python
# Written by schaefferdstudio

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser
import urlparse

import sys
import logging
import time
from websocket import create_connection
import threading
import websocket
import tempfile
import time
import sys
import os
import os.path
import alsaaudio

""" Config of Mycroft
and Speaker to shutdown
Request url with:
http://xxxxx:8090/?speak=xxx_xxx&code=xxxx
Search the speaker mycroft use with alsamixer
"""
# change that lines
port = 8090
codes = ['xxxx', 'xxxx']
cardIndex = 1
speakerName = "Speaker"


''' You do not use to change that '''

uriMycroft = 'ws://' + "localhost" + ':8181/core'
def check_for_signal(signal_name, sec_lifetime=0):
    """See if a named signal exists

    Args:
        signal_name (str): The signal's name.  Must only contain characters
            valid in filenames.
        sec_lifetime (int, optional): How many seconds the signal should
            remain valid.  If 0 or not specified, it is a single-use signal.
            If -1, it never expires.

    Returns:
        bool: True if the signal is defined, False otherwise
    """
    path = os.path.join("/tmp/mycroft/ipc/", "signal", signal_name)
    if os.path.isfile(path):
        if sec_lifetime == 0:
            # consume this single-use signal
            os.remove(path)
        elif sec_lifetime == -1:
            return True
        elif int(os.path.getctime(path) + sec_lifetime) < int(time.time()):
            # remove once expired
            os.remove(path)
            return False
        return True

    # No such signal exists
    return False

def is_speaking():
    """Determine if Text to Speech is occurring

    Returns:
        bool: True while still speaking
    """
    return check_for_signal("isSpeaking", -1)


def wait_while_speaking():
    """Pause as long as Text to Speech is still happening

    Pause while Text to Speech is still happening.  This always pauses
    briefly to ensure that any preceeding request to speak has time to
    begin.
    """
    time.sleep(0.3)  # Wait briefly in for any queued speech to begin
    while is_speaking():
        time.sleep(0.1)

class RequestHandler(BaseHTTPRequestHandler):

    waitUntilFinished = False
    res = ""
    ws = None
    m = None
    mes = ""
    def on_open(self, ws):
        #sendingMessage = self.mes.replace("_", " ");
        self.res = ws.send(self.mes)
        #res =  ws.recv()

    def on_message(self, ws, message):
        if 'utterance' in message and 'expect_response' in message:
            start = '"utterance": "'
            end = '"}, "type":'
            self.m = alsaaudio.Mixer(speakerName, cardindex=cardIndex)
            self.m.setmute(1)
            self.res = message[message.find(start)+len(start):message.rfind(end)]
            ws.close()
            self.waitUntilFinished = False



    def threadWaitFinishMute(self):
        wait_while_speaking()
        self.m.setmute(0)
        print("Finished mute")
        

    def do_GET(self):
        query_components = urlparse.parse_qs(self.path[2:])
        text = query_components["speak"][0]
        code  = query_components["code"][0]
        if code in codes:
            text = text.replace("_", " ")
            request_path = self.path
            self.mes = '{"type": "recognizer_loop:utterance", "data": {"utterances": ["' + text +  '"]}}'
            websocket.enableTrace(True)
            ws = websocket.WebSocketApp(uriMycroft, on_message = self.on_message)
            ws.on_open = self.on_open
            self.waitUntilFinished = True
            ws.run_forever()

        #print("\n----- Request Start ----->\n")
        #print(request_path, port)
        #print(self.headers)
        #print("<----- Request End -----\n")

        self.send_response(200)
        self.send_header('Content-type','text-html')
        self.end_headers()

        #send file content to client
        #
        if code in codes:
            self.wfile.write(self.res)
            t = threading.Thread(target=self.threadWaitFinishMute)
            t.daemon = True
            t.start()
        else:
            self.wfile.write("Access denied")
        #


print('Listening on localhost:%s' % port)
server = HTTPServer(('', port), RequestHandler)
server.serve_forever()
