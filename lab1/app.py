#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth

# data
songs = [
    {
        'id': 1,
        'title': '505',
        'artist': 'Arctic Monkeys'
    },
    {
        'id': 2,
        'title': 'All These Things That I\'ve Done',
        'artist': 'The Killers'
    },
    {
        'id': 3,
        'title': 'American Prayer',
        'artist': 'The Doors'
    }
]

playlists = [
    {
        'id': 1,
        'title': 'Arctic Monkeys',
        'owner': 'Tvrtko', 
        'songs': [1]
    },
    {
        'id': 2,
        'title': 'Oldies',
        'owner': 'Retro Steve', 
        'songs': [3]
    },
    {
        'id': 3,
        'title': 'Favs',
        'owner': 'Babs',
        'songs': [2, 3]
    }
]

def make_public_playlist(playlist):
    new_playlist = {}
    for field in playlist:
        if field == 'songs':
            new_playlist['songs'] = [songs[song_id - 1] for song_id in playlist[field]]
        else:
            new_playlist[field] = playlist[field]
    return new_playlist

# auth
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'admin'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

# app
app = Flask(__name__)

# playlists
@app.route('/api/playlists', methods=['GET'])
@auth.login_required
def get_playlists():
    return jsonify({'playlists': [make_public_playlist(playlist) for playlist in playlists]})

@app.route('/api/playlists/<int:playlist_id>', methods=['GET'])
@auth.login_required
def get_playlist(playlist_id):
    playlist = [playlist for playlist in playlists if playlist['id'] == playlist_id]
    if len(playlist) == 0:
        abort(404)
    return jsonify({'playlist': make_public_playlist(playlist[0])})

@app.route('/api/playlists', methods=['POST'])
@auth.login_required
def create_playlist():
    if not request.json or not 'title' or not 'owner' in request.json:
        abort(400)
    playlist = {
        'id': playlists[-1]['id'] + 1,
        'title': request.json['title'],
        'owner': request.json['owner'],
        'songs': request.json['songs']
    }
    playlists.append(playlist)
    return jsonify({'playlist': make_public_playlist(playlist)}), 201

@app.route('/api/playlists/<int:playlist_id>', methods=['PUT'])
@auth.login_required
def update_playlist(playlist_id):
    playlist = [playlist for playlist in playlists if playlist['id'] == playlist_id]
    if len(playlist) == 0:
        abort(404)
    if not request.json:
        print(request.json)
        abort(400)
    playlists[playlist_id - 1]['title'] = request.json.get('title', playlist[0]['title'])
    playlists[playlist_id - 1]['owner'] = request.json.get('owner', playlist[0]['owner'])
    playlists[playlist_id - 1]['songs'] = request.json.get('songs', playlist[0]['songs'])
    return jsonify({'playlist': make_public_playlist(playlists[playlist_id - 1])})

@app.route('/api/playlists/<int:playlist_id>', methods=['DELETE'])
@auth.login_required
def delete_playlist(playlist_id):
    playlist = [playlist for playlist in playlists if playlist['id'] == playlist_id]
    if len(playlist) == 0:
        abort(404)
    playlists.remove(playlist[0])
    return jsonify({'result': True})

# songs
@app.route('/api/songs', methods=['GET'])
@auth.login_required
def get_songs():
    return jsonify({'songs': songs})

@app.route('/api/songs/<int:song_id>', methods=['GET'])
@auth.login_required
def get_song(song_id):
    song = [song for song in songs if song['id'] == song_id]
    if len(song) == 0:
        abort(404)
    return jsonify({'song': song[0]})

@app.route('/api/songs', methods=['POST'])
@auth.login_required
def create_song():
    print(request.json)
    if not request.json or not 'title' or not 'artist' in request.json:
        abort(400)
    song = {
        'id': songs[-1]['id'] + 1,
        'title': request.json['title'],
        'artist': request.json['artist']
    }
    songs.append(song)
    return jsonify({'song': song}), 201

@app.route('/api/songs/<int:song_id>', methods=['PUT'])
@auth.login_required
def update_song(song_id):
    song = [song for song in songs if song['id'] == song_id]
    if len(song) == 0:
        abort(404)
    if not request.json:
        abort(400)
    songs[song_id - 1]['title'] = request.json.get('title', song[0]['title'])
    songs[song_id - 1]['artist'] = request.json.get('artist', song[0]['artist'])
    return jsonify({'song': songs[song_id - 1]})

@app.route('/api/songs/<int:song_id>', methods=['DELETE'])
@auth.login_required
def delete_song(song_id):
    song = [song for song in songs if song['id'] == song_id]
    
    if len(song) == 0:
        abort(404)

    for playlist in playlists:
        for playlist_song_id in songs:
            if playlist_song_id == song_id:
                playlist.songs.remove(playlist_song_id)
                break

    songs.remove(song[0])
    return jsonify({'result': True})

# songs in playlists
@app.route('/api/playlists/<int:playlist_id>/songs', methods=['GET'])
@auth.login_required
def get_playlist_songs(playlist_id):
    playlist = make_public_playlist(playlists[playlist_id - 1])
    return jsonify({'songs': playlist['songs']})

@app.route('/api/playlists/<int:playlist_id>/songs/<int:song_id>', methods=['GET'])
@auth.login_required
def get_playlist_song(playlist_id, song_id):
    playlist = make_public_playlist(playlists[playlist_id - 1])
    song = [song for song in playlist['songs'] if song['id'] == song_id]
    if len(song) == 0:
        abort(404)
    return jsonify({'song': song[0]})

@app.route('/api/playlists/<int:playlist_id>/song', methods=['POST'])
@auth.login_required
def create_playlist_song(playlist_id):
    playlist = make_public_playlist(playlists[playlist_id - 1])
    if not request.json or not 'title' or not 'artist' in request.json:
        abort(400)
    song = {
        'id': songs[-1]['id'] + 1,
        'title': request.json['title'],
        'artist': request.json['artist']
    }
    songs.append(song)
    playlist.songs.append(song['id'])
    return jsonify({'song': song}), 201

@app.route('/api/playlists/<int:playlist_id>/song/<int:song_id>', methods=['PUT'])
@auth.login_required
def update_playlist_song(playlist_id, song_id):
    playlist = make_public_playlist(playlists[playlist_id - 1])
    song = [song for song in playlist.songs if song['id'] == song_id]
    if len(song) == 0:
        abort(404)
    if not request.json:
        abort(400)
    songs[song_id - 1]['title'] = request.json.get('title', song[0]['title'])
    songs[song_id - 1]['artist'] = request.json.get('artist', song[0]['artist'])
    return jsonify({'song': songs[song_id - 1]})

@app.route('/api/playlists/<int:playlist_id>/song/<int:song_id>', methods=['DELETE'])
@auth.login_required
def delete_playlist_song(playlist_id, song_id):
    playlist = make_public_playlist(playlists[playlist_id - 1])
    song = [song for song in playlist.songs if song['id'] == song_id]
    
    if len(song) == 0:
        abort(404)

    for playlist in playlists:
        for playlist_song_id in songs:
            if playlist_song_id == song_id:
                playlist.songs.remove(playlist_song_id)
                break

    songs.remove(song[0])
    return jsonify({'result': True})

# index
@app.route('/')
def index():
    return 'GET /api/playlists</br>\
	GET /api/playlists/PLAYLIST_ID</br>\
	POST /api/playlists</br>\
	PUT /api/playlists/PLAYLIST_ID</br>\
	DELETE /api/playlists/PLAYLIST_ID</br>\
	</br>\
	GET /api/songs</br>\
	GET /api/songs/SONG_ID</br>\
	POST /api/songs</br>\
	PUT /api/songs/SONG_ID</br>\
	DELETE /api/songs/SONG_ID</br>\
	</br>\
	GET /api/playlists/PLAYLIST_ID/songs</br>\
	GET /api/playlists/PLAYLIST_ID/songs/SONG_ID</br>\
	POST /api/playlists/PLAYLIST_ID/songs</br>\
	PUT /api/playlists/PLAYLIST_ID/songs/SONG_ID</br>\
	DELETE /api/playlists/PLAYLIST_ID/songs/SONG_ID</br>'

# replaces html 404 with json
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)