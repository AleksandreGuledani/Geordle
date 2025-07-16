from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import random, sqlite3


app = Flask(__name__)
app.secret_key = 'D9S9sLUkK9OaM2OzRxu_99b57Ttv8l7U'

def choose_secret_word(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().split()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1251') as file:
            words = file.read().split()
    return random.choice(words).upper()

file_path = 'C:/Users/User/Desktop/Programming/University/Geordle/static/wordList.txt'

@app.route('/')
def index():
    secret_word = choose_secret_word(file_path)
    session['secret_word'] = secret_word
    
    
    logged_in_user = session.get('user')
    
    return render_template('index.html', logged_in_user=logged_in_user)

@app.route('/get_word_list')
def get_word_list():
    with open(file_path, encoding='utf-8') as file:
        words = [line.strip().upper() for line in file.readlines()]
    return jsonify(words)

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    guess = request.json.get('guess').upper()
    secret_word = session.get('secret_word')
    current_row = int(request.json.get('current_row'))

    if not secret_word:
        return jsonify({'message': 'Secret word not found', 'correct': False, 'redirect': False})

    colors = ['gray'] * len(guess)

    temp_secret_word = list(secret_word)
    for i in range(len(guess)):
        if guess[i] == temp_secret_word[i]:
            colors[i] = 'green'
            temp_secret_word[i] = None

    for i in range(len(guess)):
        if colors[i] != 'green' and guess[i] in temp_secret_word:
            colors[i] = 'yellow'
            temp_secret_word[temp_secret_word.index(guess[i])] = None

    
    points = 0
    if guess == secret_word:
        points = 6 - current_row  
        
        logged_in_user = session.get('user')
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET points = points + ? WHERE username = ?", (points, logged_in_user))
            conn.commit()
        
        return jsonify({'correct': True, 'redirect': True, 'colors': colors, 'points': points})
    else:
        if current_row == 5:
            return jsonify({'correct': False, 'redirect': True, 'colors': colors})
        return jsonify({'correct': False, 'redirect': False, 'colors': colors})


@app.route('/win')
def win():
    secret_word = session.get('secret_word')
    return render_template('win.html', secret_word=secret_word)

@app.route('/lose')
def lose():
    secret_word = session.get('secret_word')
    return render_template('lose.html', secret_word=secret_word)





@app.route('/about.html')
def about():
    logged_in_user = session.get('user')
    return render_template('about.html', logged_in_user=logged_in_user)

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    error_message = None 
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()

        if user:
            
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error_message = 'Invalid username or password'
    
    return render_template('login.html', error_message=error_message)

@app.route('/logout')
def logout():
    
    session.pop('user', None)
    return redirect(url_for('index'))


def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL,
                            points INTEGER DEFAULT 0)''')
        conn.commit()


init_db()



@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                
                session['user'] = username
                
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                error_message = 'Username already exists'

    return render_template('register.html', error_message=error_message)


@app.route('/profile.html')
def profile():
    logged_in_user = session.get('user')
    if logged_in_user:
        with sqlite3.connect('users.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM users WHERE username = ?", (logged_in_user,))
            user_data = cursor.fetchone()
            points = user_data[0] if user_data else 0
    else:
        points = 0  

    return render_template('profile.html', logged_in_user=logged_in_user, points=points)


@app.route('/leaderboard')
def leaderboard():
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, points FROM users ORDER BY points DESC")
        users = cursor.fetchall()

    return render_template('leaderboard.html', users=users)



if __name__ == '__main__':
    app.run(debug=True)
