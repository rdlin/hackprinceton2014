from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from pymongo import Connection
import pdb
from rdio import Rdio
from musixmatch import track

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
        if (collection.find_one({'room': room, 'username': username}) == None):
            collection.insert({'room': room, 'username': username})
            return redirect(url_for('room', room=room, username=username))
        else:
            return renderErrorInTemplate('index.html', room, username,
                                         error=' This user has already been taken for this room.')

@app.route('/room/<room>/<username>/')
def room(room, username):
    return render_template('room.html', room=room, username=username)

@app.route('/leave/<room>/<username>/', methods=['POST'])
def leave(room, username):
    collection.remove({'room': room, 'username':username})

@app.route('/sockets')
def sock():
    return render_template('test.html')

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

def filterLyrics(lyrics):
    bad_word_dict = {
        "******* This Lyrics is NOT for Commercial use *******": "",
        "fuck": "f*ck"}
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

def get_tracks_for_album(album):
    track_keys = []
    for track_key in album["trackKeys"]:
        track_keys.append(track_key)
    return get_objects_for_keys(track_keys)

def get_trending_albums(count="10"):
    search_results = rdio.call("getHeavyRotation", {"type": "albums", "count": count})
    if verify_search_results(search_results):
        return search_results["result"]

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

if __name__ == '__main__':
    set_rdio()
    app.run(debug=True)
