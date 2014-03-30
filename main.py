from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask.ext.socketio import SocketIO, send, emit, join_room, leave_room
from pymongo import Connection
import pdb
from rdio import Rdio
import random
import time
import urllib2
from musixmatch import track

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yext1234'
socketio = SocketIO(app)

# For mongoDb
connection = Connection()
db = connection['rooms-database']
collection = db['rooms']
ready = db['ready']
chosen = db['chosen']
collection.remove()
chosen.remove()
ready.remove()

# routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # process room and stuff here
        username = request.form['username']
        room = request.form['room']
        return redirect(url_for('room', room=room, username=username))

@app.route('/room/<room>/<username>/')
def room(room, username):
    if (collection.find_one({'room': room, 'username': username}) == None):
        collection.insert({'room': room, 'username': username})
        return render_template('room.html', room=room, username=username)
    else:
        return renderErrorInTemplate('index.html', room, username,
                                         error=' This user has already been taken for this room.')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    # emit('joined', room=room)
    # send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', room=room)

@app.route('/leave/<room>/<username>/', methods=['POST'])
def leave(room, username):
    collection.remove({'room': room, 'username':username})
    return ''

def renderErrorInTemplate(template, room, username, error):
    return render_template(template, room=room, username=username, error=error);

# SONG UTIL STARTS HERE
rdio = None

#Global rdio with authentication
def set_rdio():
    global rdio
    rdio = Rdio(("ucvxaju3gq3natuvp9w6uxrv", "vwnQkPkDhM"))

#endpoints, mostly for testing
@app.route("/search/<item>/<track_name>/")
def get_item_for_track_name_search(track_name=None, item=None):
    return "<br>".join(get_tracks_item_list("name", search_for_tracks(track_name)))

@app.route("/topchart/")
def get_item_string_for_top_chart_tracks(item=None):
    return "<br>".join(get_tracks_item_list("name", get_top_chart_tracks()))

#getting lyrics and a bunch of other information for a track search
@app.route("/search/<track_name>/info/")
def get_info_for_track_name_search(track_name=None):
    displayString = ""
    for track in search_for_tracks(track_name):
        displayString+="Name: " + track["name"]+"<br>"
        displayString+="Artist: " + track["artist"]+"<br>"
        displayString+="Lyrics: " + get_lyrics_for_track_name(name=track["name"], artist=track["artist"])+"<br>"
        displayString+="<br><br>"
    return displayString

#getting lyrics and a bunch of other information for a track search by artist
@app.route("/search/artist/<artist_name>/info/")
def get_info_for_track_name_by_artist_search(artist_name=None):
    displayString = ""
    for track in search_for_tracks(artist_name):
        displayString+="Name: " + track["name"]+"<br>"
        displayString+="Artist: " + track["artist"]+"<br>"
        displayString+="Lyrics: " + get_lyrics_for_track_name(name=track["name"], artist=track["artist"])+"<br>"
        displayString+="<br><br>"
    return displayString

#getting and testing album methods
@app.route("/albums/new/")
def get_new_albums_this_week():
    displayString = ""
    for album in get_new_albums():
        displayString+="Name: " + album["name"]+"<br>"
        displayString+="Artist: " + album["artist"]+"<br>"
        displayString+="Tracks: " + " , ".join([track["name"] for track in get_tracks_for_album(album)])
        displayString+="<br><br>"
    return displayString

#getting and testing album methods
@app.route("/albums/trending/")
def get_trending_albums_this_week():
    displayString = ""
    for album in get_trending_albums():
        displayString+="Name: " + album["name"]+"<br>"
        displayString+="Artist: " + album["artist"]+"<br>"
        displayString+="Tracks: " + " , ".join([track["name"] for track in get_tracks_for_album(album)])
        displayString+="<br><br>"
    return displayString

#musixmatch lyric search

def get_lyrics_for_track_name(name='', artist='', lyrics=''):
    track_result_list = track.search(q_track=name, q_artist=artist, q_lyrics=lyrics)
    result = filterLyrics(track_result_list[0].lyrics()['lyrics_body'])
    return result

@app.route("/lyrics/<name>/<artist>/")
def get_lyrics(name=None, artist=None):
    track_result_list = track.search(q_track=name, q_artist=artist)
    result = filterLyrics(track_result_list[0].lyrics()['lyrics_body'])
    return result

def getOneLineInfo(name=None, artist=None):
    one_line_soup = BeautifulSoup(urllib2.urlopen('http://www.azlyrics.com/lyrics/'+artist.lower().replace(" ","")+'/'+name.lower().replace(" ","")+'.html').read())
    pdb.set_trace()
    return one_line_soup('div')[6];

def filterLyrics(lyrics):
    bad_word_dict = {
        "******* This Lyrics is NOT for Commercial use *******": "",
        "fuck": "f*ck",
        "... />": ""}
    for bad_word in bad_word_dict.keys():
        lyrics = lyrics.replace(bad_word, bad_word_dict[bad_word])
    return lyrics

#Rdio api calls and stuff

#Track specific

@app.route("/toptracks/")
def get_top_chart_tracks(count="20"):
    #http://www.rdio.com/developers/docs/web-service/types/track/ for properties types
    top_charts_request = rdio.call("getTopCharts", {"type": "Track", "count": count})
    if (top_charts_request["status"] != "ok"):
        raise Exception("Status for getting top chart returned not ok")
    return jsonify(data=top_charts_request["result"])

@app.route('/endpoint/search/<track_name>/')
def search_track_endpoint(track_name):
    return jsonify(data=search_for_tracks(track_name));

def search_for_tracks(search_query, count="10"):
    return search_for_items("Track", search_query, count)

def search_for_tracks_by_artist(search_query, count="10"):
    search_results = rdio.call("getTracksForArtist", {"artist": search_query, "count": count})
    if (search_results["status"] != "ok"):
        raise Exception("Status for search returned not ok")
    elif (len(search_results) == 0):
        raise Exception("Search result return no results")
    return search_results["result"]["results"]

def get_tracks_item_list(item, tracklist):
    return [track[item] for track in tracklist]

def get_item_for_track(item, track):
    return track[item]

#Album specific

def search_for_albums(search_query, count="10"):
    return search_for_items("Album", search_query, count)

def get_new_albums(count="10"):
    search_results = rdio.call("getNewReleases", {"count": count})
    if verify_search_results(search_results):
        return search_results["result"]

@app.route("/newalbums/")
def get_new_albums_jsonified(count="10"):
    search_results = rdio.call("getNewReleases", {"count": count})
    if (search_results["status"] != "ok"):
        return Exception("Status for getting trending albums returned not ok")
    return jsonify(data=search_results["result"])

@app.route("/tracks/<key>")
def get_tracks_for_album_key(key=None):
    keys = []
    keys.append(key)
    return jsonify(data=get_tracks_for_album(get_objects_for_keys(keys)[0]))

def get_tracks_for_album(album):
    track_keys = []
    for track_key in album["trackKeys"]:
        track_keys.append(track_key)
    return get_objects_for_keys(track_keys)

def get_trending_albums(count="10"):
    search_results = rdio.call("getHeavyRotation", {"type": "albums", "count": count})
    if verify_search_results(search_results):
        return search_results["result"]

@app.route("/trendingalbums/")
def get_trending_albums_jsonified(count="10"):
    search_results = rdio.call("getHeavyRotation", {"type": "albums", "count": count})
    if (search_results["status"] != "ok"):
        return Exception("Status for getting trending albums returned not ok")
    return jsonify(data=search_results["result"])

#Generic

def search_for_items(item, search_query, count="10"):
    search_results = rdio.call("search", {"query": search_query, "types": item, "count": count})
    if (search_results["status"] != "ok"):
        raise Exception("Status for search returned not ok")
    elif (len(search_results) == 0):
        raise Exception("Search result return no results")
    return search_results["result"]["results"]

def get_objects_for_keys(keys):
    rdio_object_request = rdio.call("get", {"keys": ",".join(keys)})
    if (rdio_object_request["status"] != "ok"):
        raise Exception("Status for search returned not ok")
    return [rdio_object_request["result"][key] for key in keys]

def verify_search_results(search_results):
    if (search_results["status"] != "ok"):
        raise Exception("Status for search returned not ok")
    elif (len(search_results) == 0):
        raise Exception("Search result return no results")
    return True

# SONG UTIL ENDS HERE

# TESTED DONE
# Randomly chooses two players and saves those two players for that room in the database
# If there are not enough people, error message is displayed
@app.route('/room/<room_name>')
def initPairPlayers(room_name):
    # Change this number to 3 eventually
    number = 0
    for user in collection.find({'room': room_name}):
        number += 1
    if number < 3:
        return jsonify(error="There should be at least 3 people in the room for a game to start.")
    users = []
    for user in ready.find({'room': room_name}):
        users.append(user.get('data').get('username'))
    selected = random.sample(users, 2)
    # Remove the next line if you don't want calling initPairPlayers to delete the old pair
    # from the database
    chosen.remove({'room1': room_name})
    chosen.remove({'room2': room_name})

    chosen.insert({'room1': room_name, 'username': selected[0]})
    chosen.insert({'room2': room_name, 'username': selected[1]})

    return jsonify({'p1':selected[0], 'p2':selected[1]})

# TESTED DONE
counter = 0
# If a player is ready to play the game
# doesn't return anything
@socketio.on('readyPlayer')
def readyPlayer(data):
    global counter
    room, username = data.get('room'), data.get('username');
    ready.insert({'room': room, 'data':{'username': username, 'counter':counter}})
    counter += 1
    number = 0;

    for user in ready.find({'room': room}):
        number += 1
    if number >= 3:
        emit('game_ready', room);

# Once two players have been chosen, this just returns a map of those two players
@app.route('/room/<room>/get_pair')
def getPairPlayers(room):
    time.sleep(0.3)
    p1 = chosen.find_one({'room1': room})
    p2 = chosen.find_one({'room2': room})
    if p1 == None:
        return ""
    return jsonify({'p1':p1.get('username'), 'p2':p2.get('username')})

# Gets one player and returns the a pair, the person the player we are removing was previously mapped
# and one new person
# error out if no more valid players
@app.route('/room/<room>/<username>/invalid')
def resetPlayers(room, username):
    valid.remove({'room': room, 'username': username})
    user = chosen.find_one({'room': room})
    chosen.remove({'room': room})

    users = []
    for user in valid.find():
        if user.get('username') != user:
            users.append(user.get('username'))
    if len(users) <= 2:
        return jsonify(error="There should be at least 3 people who can/want to play for a game to start.")

    # pdb.set_trace()
    random.choice(users)

    # this has not been tested at all
    if (valid.find({'room': room}).count() < 2):
        return jsonify(error="There should be at least 3 people who can/want to play for a game to start.")

# TESTED DONE
# Returns a list of all players
@app.route('/room/<room_name>/all_players', methods=['POST', 'GET'])
def allPlayersInRoom(room_name):
    time.sleep(0.3)
    users = []
    for user in collection.find():
        users.append(user.get('username'))
    return jsonify(data=users)

if __name__ == '__main__':
    set_rdio()
    socketio.run(app)
