import logging, logging.config, conf
import requests
import time
import os
from flask import Flask, render_template, send_from_directory, Response, request
from flask_socketio import SocketIO, emit
from pathlib import Path
from camera import Camera
from threading import Thread, Event
from config import URL, TEXTE_ACTIVATED, TOKEN

logging.config.dictConfig(conf.dictConfig)
logger = logging.getLogger(__name__)
camera = Camera()

app = Flask(__name__)
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
thread = Thread()
thread_stop_event = Event()


@app.route("/run", methods = ['GET', 'POST'])
def entrypoint2():  
    # démarrer le flux vidéo et l'inférence
	token = TOKEN
	req = requests.post(URL, data={'request_start': token})
	camera.run()
	return render_template("stream.html", stop_button=1)


@app.route("/", methods = ['GET', 'POST'])
def entrypoint():  
	token = TOKEN
	req = requests.post(URL, data={'request_start': token})
	camera.run()
	return render_template("stream.html", stop_button=0)


@app.route("/shut", methods = ['GET', 'POST'])
def shut():
    # stopper la connexion au serveur
	req = requests.post(URL + '/stop', data={'request_stop': 'stop'})
	try:
		req = requests.post(URL + '/shutdown', data={'request_shutdown': 'shutdown'})
	except:
		os._exit(0)
	

@socketio.on('connect', namespace='/test')
def test_connect():
    # démarrage de l'inférence du texte
	global thread
	thread = socketio.start_background_task(video_feed2)

def gen(camera):
    # flux vidéo : génération par image
    while True:
        frame, _ = camera.get_frame()
        yield (b'--frame\r\n'
			   b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # flux vidéo
	return Response(gen(camera), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed2")
def video_feed2():
    # affichage texte
	def generate():
		_, number = camera.get_frame()
		yield number
	while True:
		number = next(generate())
		socketio.emit('newnumber', {'number': number}, namespace='/test')
		socketio.sleep(2)
	

@app.route("/stop", methods = ['GET', 'POST'])
def stop():
    # stoppe le flux vidéo
    if request.form['stop'] == 'stop':
        req = requests.post(
			URL + '/stop', 
			data={'request_stop': 'stop'}
		)
        return render_template('stream.html', stop_button=0)
    else:
        render_template('stream.html', stop_button=1)


if __name__=="__main__":
	socketio.run(app)