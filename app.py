from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
app.secret_key = 'oruviralpuratchiii'  # Change this to something random

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_ref = db.collection('users').document(username)
        user = user_ref.get()

        if user.exists:
            user_data = user.to_dict()
            if user_data['password'] == password:
                session['username'] = username
                session['house'] = user_data['house']
                return redirect('/vote')
            else:
                return 'Incorrect password'
        else:
            return 'User does not exist'
    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    house = session['house']

    candidates = db.collection('candidates').stream()
    common_candidates = []
    house_candidates = []

    for candidate in candidates:
        data = candidate.to_dict()
        if data['position'].lower() == 'common':
            common_candidates.append((candidate.id, data['name']))
        elif data['position'].lower() == house.lower():
            house_candidates.append((candidate.id, data['name']))

    if request.method == 'POST':
        common_vote = request.form.get('common_vote')
        house_vote = request.form.get('house_vote')

        if common_vote:
            candidate_ref = db.collection('candidates').document(common_vote)
            candidate = candidate_ref.get()
            if candidate.exists:
                candidate_ref.update({'votes': firestore.Increment(1)})

        if house_vote:
            candidate_ref = db.collection('candidates').document(house_vote)
            candidate = candidate_ref.get()
            if candidate.exists:
                candidate_ref.update({'votes': firestore.Increment(1)})

        return redirect('/thanks')

    return render_template('vote.html', username=username, house=house,
                           common_candidates=common_candidates,
                           house_candidates=house_candidates)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
