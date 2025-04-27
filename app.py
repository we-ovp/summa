from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Get candidates (you can modify these manually or load dynamically)
candidates = ['Candidate A', 'Candidate B', 'Candidate C']

@app.route('/')
def index():
    votes_ref = db.collection('votes')
    votes = {}
    for candidate in candidates:
        doc = votes_ref.document(candidate).get()
        if doc.exists:
            votes[candidate] = doc.to_dict().get('count', 0)
        else:
            votes[candidate] = 0
    return render_template('index.html', votes=votes)

@app.route('/vote', methods=['POST'])
def vote():
    selected_candidate = request.form.get('candidate')
    if selected_candidate in candidates:
        votes_ref = db.collection('votes').document(selected_candidate)
        doc = votes_ref.get()
        if doc.exists:
            current_votes = doc.to_dict().get('count', 0) + 1
        else:
            current_votes = 1
        votes_ref.set({'count': current_votes})
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
