from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask.ext.socketio import SocketIO, emit
from pymongo import Connection
import pdb

app = Flask(__name__)
app.config.update(
    SECRET_KEY='yext1234',
    DEBUG=True
)
socketio = SocketIO(app)

# For mongoDb
connection = Connection()
db = connection['rooms-database']
collection = db['rooms']

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # process room and stuff here
        username = request.form['username']
        room = request.form['room']
        if (collection.find_one({'room': room, 'username': username}) == None):
            collection.insert({'room': room, 'username': username})
            return redirect(url_for('room', room=room))
        else:
            return renderErrorInTemplate('index.html', room, username,
                                         error=' This user has already been taken for this room.')

def renderErrorInTemplate(template, room_name, username, error):
    return render_template(template, room_name=room_name, username=username, error=error);

@app.route('/room/<room_name>/')
def room(room_name):
    return render_template('room.html', room=room_name)

if __name__ == '__main__':
    if app.debug:
        app.run(debug=True)
    else:
        socketio.run(app, debug=True)
