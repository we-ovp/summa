# from flask import Flask, render_template, request, redirect
# import firebase_admin
# from firebase_admin import credentials, firestore

# app = Flask(__name__)

# # Initialize Firebase
# cred = credentials.Certificate('firebase_key.json')
# firebase_admin.initialize_app(cred)
# db = firestore.client()

# # Get candidates (you can modify these manually or load dynamically)
# candidates = ['Candidate A', 'Candidate B', 'Candidate C']

# @app.route('/')
# def index():
#     votes_ref = db.collection('votes')
#     votes = {}
#     for candidate in candidates:
#         doc = votes_ref.document(candidate).get()
#         if doc.exists:
#             votes[candidate] = doc.to_dict().get('count', 0)
#         else:
#             votes[candidate] = 0
#     return render_template('index.html', votes=votes)

# @app.route('/vote', methods=['POST'])
# def vote():
#     selected_candidate = request.form.get('candidate')
#     if selected_candidate in candidates:
#         votes_ref = db.collection('votes').document(selected_candidate)
#         doc = votes_ref.get()
#         if doc.exists:
#             current_votes = doc.to_dict().get('count', 0) + 1
#         else:
#             current_votes = 1
#         votes_ref.set({'count': current_votes})
#     return redirect('/')

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Firebase connection
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Dummy user database
users_db = {
    'student1': {'password': 'pass123', 'name': 'John Doe', 'house': 'Red House'},
    'student2': {'password': 'pass456', 'name': 'Jane Smith', 'house': 'Blue House'},
    'student3': {'password': 'pass789', 'name': 'Alex Green', 'house': 'Green House'}
}

houses = ['Red House', 'Blue House', 'Green House', 'Yellow House']

house_candidates = {
    'Red House': ['Red Candidate 1', 'Red Candidate 2'],
    'Blue House': ['Blue Candidate 1', 'Blue Candidate 2'],
    'Green House': ['Green Candidate 1', 'Green Candidate 2'],
    'Yellow House': ['Yellow Candidate 1', 'Yellow Candidate 2'],
}

common_candidates = ['School Captain - Candidate X', 'Cultural Secretary - Candidate Y', 'Sports Captain - Candidate Z']

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = users_db.get(username)

    if user and user['password'] == password:
        session['username'] = username
        session['house'] = user['house']
        session['name'] = user['name']
        return redirect('/vote')
    else:
        return "Invalid username or password. Try again."

@app.route('/vote')
def vote_page():
    if 'username' not in session:
        return redirect('/')
    house = session['house']
    return render_template('vote.html', 
                           house=house, 
                           house_candidates=house_candidates.get(house, []), 
                           common_candidates=common_candidates)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if 'username' not in session:
        return redirect('/')

    house = session['house']
    username = session['username']
    house_candidate = request.form.get('house_candidate')
    common_candidate = request.form.get('common_candidate')

    # Save house-specific vote
    if house and house_candidate:
        house_ref = db.collection('votes').document(house.lower().replace(' ', '_'))
        doc = house_ref.get()
        if doc.exists:
            current_votes = doc.to_dict().get(house_candidate, 0) + 1
            house_ref.update({house_candidate: current_votes})
        else:
            house_ref.set({house_candidate: 1})

    # Save common post vote
    if common_candidate:
        common_ref = db.collection('votes').document('common_posts')
        doc = common_ref.get()
        if doc.exists:
            current_votes = doc.to_dict().get(common_candidate, 0) + 1
            common_ref.update({common_candidate: current_votes})
        else:
            common_ref.set({common_candidate: 1})

    session.clear()
    return render_template('thankyou.html')

if __name__ == "__main__":
    app.run(debug=True)
