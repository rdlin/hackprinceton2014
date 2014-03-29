from flask import Flask
import musixmatch
from musixmatch import track
import pdb
import os
app = Flask(__name__)

@app.route("/")
def hello():
    return get_lyric_for_song_name('Stronger', 'Kanye')

def get_lyric_for_song_name(name='', artist='', lyrics=''):
    track_result_list = track.search(q_track=name, q_artist=artist, q_lyrics=lyrics)
    return track_result_list[0].lyrics()['lyrics_body']


if __name__ == "__main__":
    app.run()