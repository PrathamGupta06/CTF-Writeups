from flask import Flask, request, render_template, session, redirect, flash, url_for
from flask_session import Session
import sqlite3
import os
import bcrypt
import time

flag = os.environ.get('FLAG', 'GooseCTF{f4k3_fl4g_f0r_t3st1ng}')

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Create a database file if it doesn't exist
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Users
    c.execute('CREATE TABLE users (username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, verified BOOLEAN DEFAULT FALSE)')
    # Verification codes
    c.execute('CREATE TABLE verification_codes (username TEXT NOT NULL, code TEXT NOT NULL, expiry INTEGER NOT NULL)')
    # Password reset codes
    c.execute('CREATE TABLE reset_codes (username TEXT NOT NULL, code TEXT NOT NULL, expiry INTEGER NOT NULL)')
    # Messages
    c.execute('CREATE TABLE messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, receiver TEXT NOT NULL, message TEXT NOT NULL, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    # Create admin user with random password
    password = os.urandom(32).hex()
    c.execute('INSERT INTO users (username, email, password,verified) VALUES ("admin", "admin@warwickcyebrsoc.com", ?,true)', (hash_password(password),))
    # Add flag to admin messages
    c.execute('INSERT INTO messages (sender, receiver, message) VALUES ("admin", "admin", "Flag: ' + flag + '")')
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()
# Store sessions in memory
app.config['SESSION_TYPE'] = 'filesystem'
ss = Session(app)

def check_verified():
    username = session['username']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT verified FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result is None:
        return False
    return result[0]



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    # Check if user is already logged in
    if session.get('username') is not None:
        # Check if verified
        if not check_verified():
            flash('Please verify your email before sending messages', 'error')
            return redirect('/verify')
        # Redirect to messages page
        flash('You are already logged in', 'error')
        return redirect('/messages')
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_page():
    # Check if user is already logged in
    if session.get('username') is not None:
        # Check if verified
        if not check_verified():
            flash('Please verify your email before sending messages', 'error')
            return redirect('/verify')
        # Redirect to messages page
        flash('You are already logged in', 'error')
        return redirect('/messages')
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    # Check if user is already logged in
    if session.get('username') is not None:
        # Redirect to messages page
        flash('You are already logged in', 'error')
        return redirect('/messages')
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email,password,verified FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result is None:
        flash('Invalid username or password', 'error')
        return redirect('/login')
    if check_password(password, result[1]):
        # Set session cookie
        session['username'] = username
        if result[2] == False:
            flash('Please verify your email before sending messages', 'error')
            return redirect('/verify')
        flash('Logged in', 'success')
        return redirect('/messages')
    flash('Invalid username or password', 'error')
    return redirect('/login')

@app.route('/register', methods=['POST'])
def register():
    # Check if user is already logged in
    if 'username' in session:
        # Redirect to messages page
        flash('You are already logged in', 'error')
        return redirect('/messages')
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Check if username or email already exists
    c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    result = c.fetchone()
    if result is not None:
        flash('Username or email already exists', 'error')
        return redirect('/register')
    c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hash_password(password)))
    # Generate verification code
    code = os.urandom(16).hex()
    c.execute('INSERT INTO verification_codes (username, code, expiry) VALUES (?, ?, ?)', (username, code, int(time.time()) + 60 * 60))
    send_verification_email(email, code)
    # Create welcome message
    c.execute('INSERT INTO messages (sender, receiver, message) VALUES ("admin", ?, "Welcome to cyber soc messenger!")', (username,))
    conn.commit()
    conn.close()
    # Set session cookie
    session['username'] = username

    flash('Account created. Please verify your email', 'success')
    return redirect('/verify')

@app.route('/send', methods=['POST'])
def send():
    sender = session['username']
    if sender is None:
        # Redirect to login page and display error message
        flash('You must be logged in to send a message', 'error')
        return redirect('/')
    if not check_verified():
        flash('Please verify your email before sending messages', 'error')
        return redirect('/verify')
    receiver = request.form['receiver']
    message = request.form['message']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)', (sender, receiver, message))
    conn.commit()
    conn.close()
    flash('Message sent', 'success')
    return redirect('/messages')

@app.route('/messages', methods=['GET'])
def messages():
    # Check if user is logged in
    if 'username' not in session:
        # Redirect to login page and display error message
        flash('You must be logged in to view messages', 'error')
        return redirect('/')
    if not check_verified():
        flash('Please verify your email before sending messages', 'error')
        return redirect('/verify')
    username = session['username']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT receiver,sender,message,time FROM messages WHERE receiver = ? or sender = ? ORDER BY time DESC', (username, username))
    result = c.fetchall()
    conn.close()

    class Message:
        def __init__(self, sender, receiver, message, time):
            self.sender = sender
            self.receiver = receiver
            self.message = message
            self.time = time

    class Thread:
        def __init__(self, id, message):
            self.id = id
            self.last_message = message
            self.messages = []
            self.messages.append(message)

    # Split messages into senders
    threads = {}
    # Get all threads and last message
    for row in result:
        sender = row[1]
        receiver = row[0]
        message = row[2][:40] + '...' if len(row[2]) > 40 else row[2]
        time = row[3]
        id = sender if sender != username else receiver
        if id not in threads:
            threads[id] = Thread(id, Message(sender, receiver, message, time))
        else:
            threads[id].messages.append(Message(sender, receiver, message, time))

    flaskThreads = []
    for key in threads:
        flaskThreads.append(threads[key])
    return render_template('messages.html', threads=flaskThreads)

@app.route('/messages/<username>', methods=['GET', 'POST'])
def view_messages(username):
    if 'username' not in session:
        flash('You must be logged in to view messages', 'error')
        return redirect('/login')
    if not check_verified():
        flash('Please verify your email before sending messages', 'error')
        return redirect('/verify')
    if request.method == 'POST':
        message = request.form['message']
        if not message:
            flash('Please enter a message', 'error')
            return redirect(f'/messages/{username}')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)', (session['username'], username, message))
        conn.commit()
        conn.close()
        return redirect(f'/messages/{username}')
    else:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT sender,receiver,message,time FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) ORDER BY time', (session['username'], username, username, session['username']))
        result = c.fetchall()
        conn.close()
        messages = []
        for row in result:
            messages.append({'sender': row[0], 'receiver': row[1], 'message': row[2], 'time': row[3]})
        return render_template('view_messages.html', messages=messages, username=username)



@app.route('/new-chat', methods=['GET', 'POST'])
def new_chat():
    if 'username' not in session:
        flash('You must be logged in to start a new chat', 'error')
        return redirect('/login')
    if not check_verified():
        flash('Please verify your email before sending messages', 'error')
        return redirect('/verify')
    if request.method == 'POST':
        username = session['username']
        receiver = request.form['username']
        message = request.form['message']
        if not receiver:
            flash('Please enter a receiver')
            return redirect('/new-chat')
        if not message:
            flash('Please enter a message')
            return redirect('/new-chat')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)', (username, receiver, message))
        conn.commit()
        conn.close()
        flash('Message sent', 'success')
        return redirect('/messages')
    return render_template('new_chat.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect('/')

@app.route('/verify', methods=['GET'])
def verify_page():
    if 'username' not in session:
        flash('You must be logged in to verify your email', 'error')
        return redirect('/')
    return render_template('verify.html')

@app.route('/verify', methods=['POST'])
def verify():
    if 'username' not in session:
        flash('You must be logged in to verify your email', 'error')
        return redirect('/')
    if check_verified():
        flash('Your email is already verified', 'error')
        return redirect('/messages')
    username = session['username']
    code = request.form['code']
    if not code:
        flash('Please enter a verification code', 'error')
        return redirect('/verify')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT expiry FROM verification_codes WHERE username = ? and code = ?', (username, code))
    result = c.fetchone()
    if result is None:
        flash('Invalid verification code', 'error')
        return redirect('/verify')
    if result[0] < int(time.time()):
        flash('Verification code has expired. Please request a new one', 'error')
        return redirect('/verify')
    c.execute('UPDATE users SET verified = true WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    flash('Email verified', 'success')
    return redirect('/messages')

@app.route('/resend', methods=['POST'])
def resend():
    if 'username' not in session:
        flash('You must be logged in to resend a verification code', 'error')
        return redirect('/')
    if check_verified():
        flash('Your email is already verified', 'error')
        return redirect('/messages')
    username = session['username']
    code = os.urandom(16).hex()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Get email
    c.execute('SELECT email FROM users WHERE username = ?', (username,))
    email = c.fetchone()[0]
    # Add new verification code
    c.execute('INSERT INTO verification_codes (username, code, expiry) VALUES (?, ?, ?)', (username, code, int(time.time()) + 60 * 60))
    conn.commit()
    conn.close()
    send_verification_email(email, code)
    flash('Verification code sent', 'success')
    return redirect('/verify')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Check if username exists
        c.execute('SELECT email FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        if result is None:
            flash('Invalid username', 'error')
            return redirect('/reset-password')
        # Create reset code
        code = os.urandom(16).hex()
        c.execute('INSERT INTO reset_codes (username, code, expiry) VALUES (?, ?, ?)', (username, code, int(time.time()) + 60 * 60))
        conn.commit()
        conn.close()
        send_reset_password_email(result[0], code)
        flash('Password reset email sent', 'success')
        session['reset_username'] = username
        return redirect('/set-password')
    return render_template('reset_password.html')

@app.route('/set-password', methods=['GET', 'POST'])
def set_password():
    if request.method == 'POST':
        username = request.form['username']
        code = request.form['code']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT expiry FROM reset_codes WHERE code = ?', (code,))
        result = c.fetchone()
        if result is None:
            flash('Invalid reset code', 'error')
            return redirect('/set-password')
        if result[0] < int(time.time()):
            flash('Reset code has expired. Please request a new one', 'error')
            return redirect('/reset-password')
        c.execute('UPDATE users SET password = ? WHERE username = ?', (hash_password(password), username))
        c.execute('DELETE FROM reset_codes WHERE code = ?', (code,))
        conn.commit()
        conn.close()
        flash('Password reset', 'success')
        return redirect('/login')
    # Get username from session
    if 'reset_username' in session:
        return render_template('set_password.html', username=session['reset_username'])
    else:
        return redirect('/reset-password')

def send_reset_password_email(email, code):
    # Send email
    import smtplib

    server = smtplib.SMTP('127.0.0.1', 8025)
    subject = 'Reset your password'
    body = f'Your password reset code is: {code}'
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail('messenger@warwickcybersoc.com', email, message)
    server.quit()

# Email
def send_verification_email(email, code):
    # Send email
    import smtplib

    server = smtplib.SMTP('127.0.0.1', 8025)
    subject = 'Verify your email'
    body = f'Your verification code is: {code}'
    message = f'Subject: {subject}\n\n{body}'
    server.sendmail('messenger@warwickcybersoc.com', email, message)
    server.quit()

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





