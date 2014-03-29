from flask import Flask
from musixmatch import track
import pdb
from rdio import Rdio

app = Flask(__name__)

@app.route("/")
def hello():
    return ', '.join(get_property_from_top_chart("icon"))

def get_lyrics_for_song_name(name='', artist='', lyrics=''):
    track_result_list = track.search(q_track=name, q_artist=artist, q_lyrics=lyrics)
    return track_result_list[0].lyrics()['lyrics_body']

def get_property_from_top_chart(property):
    #pdb.set_trace()
    rdio = Rdio(("ucvxaju3gq3natuvp9w6uxrv", "vwnQkPkDhM"))
    topChartsRequest = rdio.call("getTopCharts", {"type": "Track"})
    if (topChartsRequest["status"] != "ok"):
        raise Exception("Status returned not ok")
    top_items = []
    for top_item in topChartsRequest["result"]:
        top_items.append(top_item[property])
    return top_items

if __name__ == "__main__":
    app.run()