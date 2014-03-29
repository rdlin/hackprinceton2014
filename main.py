from flask import Flask
from flask import render_template
from flask import request
from flask.ext.socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yext1234'
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        print 'hello world'

if __name__ == '__main__':
    socketio.run(app)
