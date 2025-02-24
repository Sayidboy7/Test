from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.permanent_session_lifetime = timedelta(hours=12)

db = SQLAlchemy()

db.init_app(app)


class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(40), nullable=False)
	password = db.Column(db.String(20), nullable=False)

	def __init__(self, name, email, password):
		self.name = name
		self.email = email
		self.password = password

	def __repr__(self):
		return f'{self.id} | {self.name}'


class Note(db.Model):
	__tablename__ = 'notes'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100))
	note_content = db.Column(db.String(250))
	created_at = db.Column(db.DateTime(), default = datetime.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	user = db.relationship('User', backref='notes')


	def __init__(self, username, note_content, user_id):
		self.username = username
		self.note_content = note_content
		self.user_id = user_id

		
	def __repr__(self):
		return f'{self.id} | {self.note_content}'


@app.route('/')
def home():
	session.permanent = True
	if 'email' in session:
		title = 'Home'
		return render_template('base.html', title=title)

	return redirect(url_for('login'))

@app.route('/about')
def about():
	title = 'About'
	return render_template('about.html',title=title)


@app.route('/contact')
def contact():
	title = 'Contact'
	return render_template('contact.html', title=title)


@app.route('/register', methods=['POST', 'GET'])
def register():
	title = 'Register'
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']

		user = User.query.filter_by(email=email).first()

		if not name or not email or not password:
			flash('Please complete the form!', category='error')
			return redirect(url_for('register'))
		else:
			if user:
				flash('This Email already registered', category='error')
				return redirect(url_for('register'))
			else:
				user = User(name, email, password)

				db.session.add(user)
				db.session.commit()
			
				
		return redirect(url_for('login'))

	else:
		return render_template('register.html', title = title)


@app.route('/login', methods = ['POST', 'GET'])
def login():
	if 'name' not in session:
		title = 'Login'
		if request.method == 'POST':
			email = request.form['email']
			password = request.form['password']

			user = User.query.filter_by(email=email, password=password).first()

			if user:
				flash('You are Loginned Successfully!', category='success')
				session['email'] = email
				return redirect(url_for('home'))
			else:
				flash('Incorrect email or password', category='error')
				return redirect(url_for('login'))

		return render_template('login.html', title = title)

	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('email', None)
	return redirect(url_for('login'))


@app.route('/notes', methods = ['POST', 'GET'])
def notes():
	title = 'Notes'
	notes = Note.query.all()
	if request.method == 'POST':
		note = request.form['note_content']
		name = request.form['name']

		user = User.query.filter_by(name=name).first()

		if user:
			user_id = user.id
		else:
			flash('Foydalanuchi mavjud emas', category='error')
			return redirect(url_for('contact'))

		if not note or not name:
			flash('Please complete the form', category='error')

		else:
			note = Note(name,note, user_id)

			db.session.add(note)
			db.session.commit()
		
			flash('You\'re Note Saved Successfully!', category='success')

			return redirect(url_for('notes'))

		return redirect(url_for('contact'))
	else:
		return render_template('notes.html', notes=notes, title=title)


@app.route('/note', methods=['POST', 'GET'])
def note():
	if request.method == 'POST':
		if 'email' in session:
			note = request.form.get('note_content')
			email = session['email']

			user = User.query.filter_by(email=email).first()

			if user:
				user_id = user.id
			else:
				flash('Foydalanuvchi mavjud emas', category='error')
				return redirect(url_for('home'))

			if not note:
				flash('Please complete the form.', category='error')

			else:
				note = Note(email, note, user_id)

				db.session.add(note)
				db.session.commit()

				flash('You\'re Note Saved Successfully!', category='success')

			return redirect(url_for('notes'))

	return redirect(url_for('home'))

	
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)