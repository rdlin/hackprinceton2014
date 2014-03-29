from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from pymongo import Connection
import pdb

app = Flask(__name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yext1234'

# For mongoDb
connection = Connection()
db = connection['rooms-database']
collection = db['rooms']
collection.remove()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # process room and stuff here
        username = request.form['username']
        room = request.form['room']
        return redirect(url_for('room', room_name=room, username=username))

def renderErrorInTemplate(template, room_name, username, error):
    return render_template(template, room_name=room_name, username=username, error=error);

@app.route('/room/<room_name>/<username>/')
def room(room_name, username):
    if (collection.find_one({'room': room_name, 'username': username}) == None):
        collection.insert({'room': room_name, 'username': username})
        return render_template('room.html', room_name=room_name, username=username)
    else:
        return renderErrorInTemplate('index.html', room_name, username,
                                         error=' This user has already been taken for this room.')

@app.route('/leave/<room_name>/<username>/', methods=['POST'])
def leave(room_name, username):
    collection.remove({'room': room_name, 'username':username})

@app.route('/sockets')
def sock():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)
