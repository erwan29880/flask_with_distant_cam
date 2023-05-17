from flask import Flask, jsonify, request, Response
import socket
import cv2
import sys
import pickle
import struct
import imutils
import time
import threading 
import os
from config import TOKEN, PORT

app = Flask(__name__)

class Run_webcam():
    
    """
    envoie un flux webcam par socket
    """
    
    def __init__(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host_name  = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.port = PORT
        self.socket_address = (self.host_ip, self.port)
        self.server_socket.bind(self.socket_address)
        self.client_socket = None
        self.event = None
        self.event2 = None
        self.t1 = None

    def run(self) -> bool:
        # ouvre le flux webcam, envoie des bytes par socket
        
        print('run')
        if self.client_socket == None:
            self.server_socket.listen(1)
            self.client_socket,addr = self.server_socket.accept()
        else:
            print('accept')
        
        vid = cv2.VideoCapture(0)
        while(vid.isOpened()):
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            self.client_socket.sendall(message)
            if self.event.is_set():
                vid.release()
                self.server_socket.shutdown(1)
                print('webcam stopped')
                break
        return False
                

    def set_thread(self) -> None:
        # fermeture/ouverture à distance du flux webcam
        self.t1 = threading.Thread(target = self.run)
        self.t2 = threading.Thread(target = self.shut)
        self.event = threading.Event()
        self.event2 = threading.Event()
        self.t1.start()
        self.t2.start()
    
    
    def shut(self) -> None:
        while True:
            if self.event2.is_set():
                self.server_socket.shutdown(0)
                self.server_socket.close()
                sys.exit()    
        

cl = Run_webcam()


@app.route("/", methods = ['GET','POST'])
def entrypoint2():
    global cl
    token = TOKEN
    if request.form['request_start']  == token:
        cl.set_thread()
        return jsonify({'status thread run serveur':'ok'})    
    else:
        return jsonify({'status thread run serveur':'failed'})    
        

@app.route("/stop", methods = ['GET','POST'])
def stop():
    global cl
    if request.form['request_stop']  == 'stop':
        cl.event.set()
        return jsonify({'stop':'stopped'})
    else:
        return jsonify({'stop':'failed'})


@app.route("/shutdown", methods = ['GET','POST'])
def shut():
    cl.event2.set()
    time.sleep(3)
    if request.form['request_shutdown']  == 'shutdown':
        os._exit(0)


@app.route("/test")
def test():
    return jsonify({"runing":'True'})


if __name__=="__main__":
    app.run(host='0.0.0.0', port=5002)