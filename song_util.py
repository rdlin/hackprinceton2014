from flask import Flask
from musixmatch import track
import pdb
from rdio import Rdio

app = Flask(__name__)

#endpoints, mostly for testing

@app.route("/")
def get_names_string():
    return "Hello World"

@app.route("/<track_name>/<item>")
def get_item_for_track_name(track_name=None, item=None):
    return "<br>".join([track[item] for track in search_for_tracks(track_name)])

@app.route("/<item>")
def get_item_string_for_top_chart_tracks(item=None):
    top_chart_tracks = get_top_chart_tracks()
    if(item not in top_chart_tracks[0].keys()):
        raise Exception("Invalid item for track." + 
            "consult http://www.rdio.com/developers/docs/web-service/types/track/ for proper types")
    return "<br>".join(get_top_chart_tracks_items(item, top_chart_tracks))

#musixmatch lyric search

def get_lyrics_for_song_name(name='', artist='', lyrics=''):
    track_result_list = track.search(q_track=name, q_artist=artist, q_lyrics=lyrics)
    return track_result_list[0].lyrics()['lyrics_body']

#Rdio api calls and stuff

def get_top_chart_tracks(count="20"):
    #http://www.rdio.com/developers/docs/web-service/types/track/ for properties types
    rdio = Rdio(("ucvxaju3gq3natuvp9w6uxrv", "vwnQkPkDhM"))
    top_charts_request = rdio.call("getTopCharts", {"type": "Track", "count": count})
    if (top_charts_request["status"] != "ok"):
        raise Exception("Status for getting top chart returned not ok")
    return top_charts_request["result"]

def search_for_tracks(search_query):
    rdio = Rdio(("ucvxaju3gq3natuvp9w6uxrv", "vwnQkPkDhM"))
    search_results = rdio.call("search", {"query": search_query, "types": "Track"})
    if (search_results["status"] != "ok"):
        raise Exception("Status for search returned not ok")
    elif (len(search_results) == 0):
        raise Exception("Search result return no results")
    return search_results["result"]["results"]

def get_top_chart_tracks_item(item, index, top_chart_tracks):
    return top_chart_tracks[index][item]

def get_top_chart_tracks_items(item, top_chart_tracks):
    return [track[item] for track in top_chart_tracks]

def get_item_for_search_for_tracks(track_name="", item=""):
    return [track[item] for track in search_for_tracks(track_name)]

if __name__ == "__main__":
    app.run()