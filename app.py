from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import re
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/softskillsdb"
app.secret_key = 'your_secret_key'

mongo = PyMongo(app)

# Dummy email sending function
def send_email(to_email, subject, body):
    sender_email = "your_email@gmail.com"
    sender_password = "your_email_password"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember_me')
        
        user = mongo.db.users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get('role', 'user')
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('Email already exists')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='sha256')
        mongo.db.users.insert_one({'full_name': full_name, 'email': email, 'password': hashed_password, 'role': role})
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return render_template('dashboard.html', user=user)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    users = mongo.db.users.find()
    return render_template('admin_dashboard.html', users=list(users))

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('chatbot.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address')
            return redirect(url_for('forgot_password'))
        
        user = mongo.db.users.find_one({'email': email})
        if not user:
            flash('Email not found')
            return redirect(url_for('forgot_password'))
        
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        mongo.db.reset_tokens.insert_one({'email': email, 'token': token})
        
        reset_url = url_for('password_reset', token=token, _external=True)
        subject = "Password Reset Request"
        body = f"To reset your password, click the following link:\n{reset_url}"
        
        send_email(email, subject, body)
        flash('Password reset email sent')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    reset_token = mongo.db.reset_tokens.find_one({'token': token})
    if not reset_token:
        flash('Invalid or expired token')
        return redirect(url_for('login'))
    
    email = reset_token['email']
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('password_reset', token=token))
        
        hashed_password = generate_password_hash(new_password, method='sha256')
        mongo.db.users.update_one({'email': email}, {'$set': {'password': hashed_password}})
        mongo.db.reset_tokens.delete_one({'token': token})
        flash('Password updated successfully')
        return redirect(url_for('login'))
    
    return render_template('password_reset.html', token=token)

@app.route('/vocabulary_lessons')
def vocabulary_lessons():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    lessons = mongo.db.lessons.find({'type': 'vocabulary'})
    return render_template('vocabulary_lessons.html', lessons=list(lessons))

if __name__ == '__main__':
    app.run(debug=True)