from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
app.secret_key = 'a-very-secret-key-change-this'  # Change this in real deployment

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('vote'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ref = db.collection('users').document(username)
        user = user_ref.get()

        if user.exists:
            user_data = user.to_dict()
            if user_data['password'] == password:
                session['user'] = username
                session['house'] = user_data['house']
                return redirect(url_for('vote'))
            else:
                return render_template('login.html', error='Invalid password.')
        else:
            return render_template('login.html', error='User does not exist.')

    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'user' not in session:
        return redirect(url_for('login'))

    house = session['house']
    common_candidates = db.collection('candidates').document('common').get()
    house_candidates = db.collection('candidates').document(house).get()

    common_list = common_candidates.to_dict().get('candidates', []) if common_candidates.exists else []
    house_list = house_candidates.to_dict().get('candidates', []) if house_candidates.exists else []

    if request.method == 'POST':
        selected_common = request.form.get('common_candidate')
        selected_house = request.form.get('house_candidate')

        vote_data = {
            'user': session['user'],
            'house': house,
            'common_vote': selected_common,
            'house_vote': selected_house
        }
        db.collection('votes').document(session['user']).set(vote_data)

        return redirect(url_for('thanks'))

    return render_template('vote.html', common_list=common_list, house_list=house_list, house=house)

@app.route('/thanks')
def thanks():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('thanks.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
