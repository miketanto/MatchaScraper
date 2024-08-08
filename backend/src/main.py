from flask import Flask, request, jsonify
from flask_cors import CORS
from llm import convert_playlist
import os

app = Flask(__name__)
CORS(app)

@app.route('/convert_playlist', methods=['POST'])
def convert_youtube_playlist():
    spotify_token = request.json['spotifyToken']
    youtube_url = request.json['youtubeUrl']
    # Call helper function to upload to YouTube
    success = convert_playlist(spotify_token,youtube_url)
    message = success.content
    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'message': 'Upload failed'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)