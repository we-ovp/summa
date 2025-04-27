from flask import Flask, render_template, request, redirect, session
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
app.secret_key = 'oruviralpuratchiii'  # change this to anything random

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users_ref = db.collection('users')
        user_doc = users_ref.document(username).get()

        if user_doc.exists:
            user = user_doc.to_dict()
            if user['password'] == password:
                session['username'] = username
                session['house'] = user.get('house', '')
                return redirect('/vote')
        
        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    house = session['house']

    candidates_ref = db.collection('candidates')
    candidates = candidates_ref.stream()

    common_candidates = []
    house_candidates = []

    for candidate in candidates:
        c = candidate.to_dict()
        if c.get('position') == "Common":
            common_candidates.append({'id': candidate.id, 'name': c['name']})
        elif c.get('position') == house:
            house_candidates.append({'id': candidate.id, 'name': c['name']})

    if request.method == 'POST':
        common_vote = request.form.get('common_vote')
        house_vote = request.form.get('house_vote')

        if common_vote:
            candidate_ref = candidates_ref.document(common_vote)
            candidate_ref.update({"votes": firestore.Increment(1)})

        if house_vote:
            candidate_ref = candidates_ref.document(house_vote)
            candidate_ref.update({"votes": firestore.Increment(1)})

        return redirect('/thanks')

    return render_template('vote.html', username=username, house=house, common_candidates=common_candidates, house_candidates=house_candidates)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
