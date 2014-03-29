from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.config.update(
    SECRET_KEY='yext1234',
    DEBUG=True
)
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # process room and stuff here
        room = request.form['room']
        return redirect(url_for('room', room_name=room))

@app.route('/room/<room_name>/')
def room(room_name):
    return render_template('room.html', room=room_name)

if __name__ == '__main__':
    if app.debug:
        app.run(debug=True)
    else:
        socketio.run(app, debug=True)
