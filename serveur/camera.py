import cv2
import socket
import threading
import time
import logging
import socket 
import pickle 
import struct 
import imutils 
import numpy as np
import torch
import requests
from config import HOST_PUBLIC_URL, SOCKET_PORT, TEXTE_ACTIVATED, LABELS, TOKEN, MODEL
from typing import Tuple

logger = logging.getLogger(__name__)
thread = None


class Camera:
    
	"""  
		gestion du flux vidéo et inférence
 	"""
    
	def __init__(self, fps:int = 20, video_source:int = 0) -> None:
		logger.info(f"Initializing camera class with {fps} fps and video_source={video_source}")
		self.fps = fps
		self.video_source = video_source
		self.max_frames = 5*self.fps
		self.frm = []
		self.isrunning = False
		self.client_socket = None
		self.host_name = HOST_PUBLIC_URL
		self.port = SOCKET_PORT
		self.labels = LABELS
		self.font = cv2.FONT_HERSHEY_PLAIN
		self.confidence = 0.52
		self.colors = np.random.uniform(0, 255, size=(2, 3))
		self.model_yolo = torch.hub.load('ultralytics/yolov5','custom', path=MODEL)
		self.texte= ""
		self.token = TOKEN


	def connect(self) -> None:
		# connection au socket serveur webcam
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect((self.host_name, self.port))


	def run(self) -> None:
		# démarrage de la détection
		logging.debug("Perparing thread")
		global thread
		if thread is None:
			logging.debug("Creating thread")
			thread = threading.Thread(target=self._capture_loop,daemon=True)
			logger.debug("Starting thread")
			self.isrunning = True
			thread.start()
			logger.info("Thread started")


	def _capture_loop(self) -> None:
		# inférence     
		dt = 1/self.fps
		logger.debug("Observation started")
		while self.isrunning:
			data = b""
			payload_size = struct.calcsize("Q")
			self.connect()

			# boucle de détection
			while True:
				while len(data)<payload_size:
					packet = self.client_socket.recv(4*1024)
					if not packet:break 
					data+=packet 

				packed_img_size = data[:payload_size]
				data = data[payload_size:]
				msg_size = struct.unpack("Q", packed_img_size)[0]
				
				while len(data)<msg_size:
					data+=self.client_socket.recv(4*1024)
				frame_data = data[:msg_size]
				data = data[msg_size:]
				frm = pickle.loads(frame_data)

				# yolo stuff
				boxes = []
				class_ids = []
				results = self.model_yolo(frm)

				for i in range(0,len(results.pred[0])) :
					# récupérer prédictions et coordonnées des carrés
					if results.pred[0][i,4] > self.confidence :
						x = int(results.pred[0][i,0])
						y = int(results.pred[0][i,1])
						w = int(results.pred[0][i,2])
						h = int(results.pred[0][i,3])
						box = np.array([x, y, w, h])
						boxes.append(box)
						class_ids.append(int(results.pred[0][i,5]))

				for box, classid in zip(boxes,class_ids):
					# affichage des carrés et des prédictions
					color = self.colors[int(classid) % len(self.colors)]
					cv2.rectangle(frm, box, color, 2)
					cv2.rectangle(frm, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
					cv2.putText(frm, self.labels[classid], (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))

				if TEXTE_ACTIVATED:
					self.texte = 'uniforme vérifié' if (0 in class_ids and 3 in class_ids and not 1 in class_ids and not 2 in class_ids) else 'uniforme non vérifié'
				
				if len(self.frm)==self.max_frames:
					self.frm = self.frm[1:]
				self.frm.append(frm)
			time.sleep(dt)
			logger.info("Thread stopped successfully")


	def stop(self) -> None:
		logger.debug("Stopping thread")
		self.isrunning = False


	def get_frame(self, _bytes:bool = True) -> Tuple[(bytes, str)]:
		# renvoie images et texte
		if len(self.frm)>0:
			if _bytes:
				img = cv2.imencode('.png',self.frm[-1])[1].tobytes()
			else:
				img = self.frm[-1]
		else:
			with open("static/not_found.jpeg","rb") as f:
				img = f.read()
		
		return img, self.texte
		