from flask import Flask, render_template, request, redirect, url_for, session
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey' 
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''


client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
def get_random_track(playlist_id):
    if playlist_id:
        tracks = sp.playlist_tracks(playlist_id, limit=50)['items']
        random_track = random.choice(tracks)
        track_info = {
            'name': random_track['track']['name'],
            'artist': random_track['track']['artists'][0]['name'],
            'preview_url': random_track['track']['preview_url']
        }
        return track_info
    return None

def get_quiz_options(correct_answer, all_tracks):
    options = [correct_answer]
    num_tracks = min(len(all_tracks), 4)
    while len(options) < num_tracks:
        random_track = random.choice(all_tracks)
        random_option = f"{random_track['track']['name']} by {random_track['track']['artists'][0]['name']}"
        if random_option not in options:
            options.append(random_option)
    random.shuffle(options)
    return options

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    session['quiz_score'] = 0
    session['quiz_attempts'] = 0

    playlist_link = request.form.get('playlist_link')
    playlist_id = playlist_link.split('/')[-1].split('?')[0]
    session['playlist_id'] = playlist_id

    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    playlist_id = session.get('playlist_id')
    quiz_score = session.get('quiz_score', 0)
    quiz_attempts = session.get('quiz_attempts', 0)
    feedback = None

    if request.method == 'POST':
        user_answer = request.form.get('user_answer', '').strip().lower()
        correct_answer = request.form.get('correct_answer', '').strip().lower()
        
        if user_answer == correct_answer:
            quiz_score += 1
            feedback = "Correct!"
        else:
            feedback = f"Wrong! The correct answer was: {correct_answer}"
        
        quiz_attempts += 1
        session['quiz_score'] = quiz_score
        session['quiz_attempts'] = quiz_attempts

        if quiz_attempts >= 3:
            return redirect(url_for('show_quiz_score'))

    track_info = get_random_track(playlist_id)
    if track_info:
        tracks = sp.playlist_tracks(playlist_id, limit=50)['items']
        correct_answer = f"{track_info['name']} by {track_info['artist']}"
        options = get_quiz_options(correct_answer, tracks)

        return render_template('quiz.html', track_info=track_info, options=options, quiz_attempts=quiz_attempts, quiz_score=quiz_score, feedback=feedback, correct_answer=correct_answer)
    else:
        return render_template('error.html', message='Error: Unable to fetch track from playlist.')

@app.route('/quiz_score')
def show_quiz_score():
    quiz_score = session.get('quiz_score', 0)
    return render_template('score.html', quiz_score=quiz_score)

if __name__ == '__main__':
    app.run(debug=True)
