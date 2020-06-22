import socketio
import eventlet
import numpy as np
from flask import Flask # flask is a python micro framework used to build webapps
from keras.models import load_model # to load our model
import base64
from io import BytesIO
from PIL import Image
import cv2

# in our case we will establish bidirectional communication with simulator
sio = socketio.Server() # websockets help in real time communication between client and server

app = Flask(__name__) #'__main__'
speed_limit = 10
def img_preprocess(img):
    img = img[60:135,:,:]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
    img = cv2.GaussianBlur(img,  (3, 3), 0)
    img = cv2.resize(img, (200, 66))
    img = img/255
    return img


@sio.on('telemetry')
def telemetry(sid, data): #as soon as connection established..following values passed
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image']))) #decoding img #buffer module = BytesIO
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print('{} {} {}'.format(steering_angle, throttle, speed))
    send_control(steering_angle, throttle) # sent to simulator



@sio.on('connect')  # to register an event handler #can use connect/disconnect/message
def connect(sid, environ): #session id=sid
    print('Connected') # print connected as soon as we open simulator in autonomous mode
    send_control(0, 0)

def send_control(steering_angle, throttle):
    sio.emit('steer', data = { # steer is the custom event
        'steering_angle': steering_angle.__str__(), #imp to use it as string for our simulator
        'throttle': throttle.__str__()
    })


if __name__ == '__main__':
    model = load_model('model.h5')
    app = socketio.Middleware(sio, app) # combine socketio server(sio) with flask webapp
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app) # wsgi server help to send any request made by client direct to the server
    # ip address remains empty so that it can listen on any server # port shoud be 4567
