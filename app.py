from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_super_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# ---------------------
# Database Models
# ---------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ---------------------
# Routes
# ---------------------

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'danger')
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['user'])

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['user']).first()

    if request.method == 'POST':
        msg = request.form['message']
        feedback_entry = Feedback(message=msg, user=user)
        db.session.add(feedback_entry)
        db.session.commit()
        flash('Feedback received! Thank you.', 'success')
        return render_template('feedback.html', message=msg)

    return render_template('feedback.html', message=None)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# ---------------------
# Run the app
# ---------------------

if __name__ == '__main__':
    app.run(debug=True)
