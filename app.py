from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Create uploads directory for profile pictures
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if not username or not email or not password:
            flash("All fields are required.")
            return render_template('register.html')

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash("Username already exists.")
            conn.close()
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
        conn.commit()
        conn.close()
        flash("Registration successful. Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if not user:
        conn.close()
        flash("User not found.")
        return redirect(url_for('login'))

    # Fetch user posts
    posts = conn.execute('SELECT * FROM posts WHERE user_id = ? ORDER BY timestamp DESC',
                         (session['user_id'],)).fetchall()

    conn.close()

    return render_template('dashboard.html', user=user, posts=posts)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_public = 1 if 'is_public' in request.form else 0
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute('INSERT INTO posts (user_id, title, content, is_public, timestamp) VALUES (?, ?, ?, ?, ?)',
                     (session['user_id'], title, content, is_public, timestamp))
        conn.commit()
        conn.close()

        flash("Post created successfully!")
        return redirect(url_for('dashboard'))

    return render_template('create.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ? AND user_id = ?', 
                        (post_id, session['user_id'])).fetchone()

    if not post:
        conn.close()
        flash("Post not found.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_public = 1 if 'is_public' in request.form else 0

        conn.execute('UPDATE posts SET title = ?, content = ?, is_public = ? WHERE id = ?',
                     (title, content, is_public, post_id))
        conn.commit()
        conn.close()

        flash("Post updated successfully.")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ? AND user_id = ?', 
                        (post_id, session['user_id'])).fetchone()

    if post:
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        flash("Post deleted.")
    else:
        flash("Post not found or unauthorized.")

    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def comment(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    content = request.form['content']
    user_id = session['user_id']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO comments (user_id, post_id, content) VALUES (?, ?, ?)',
        (user_id, post_id, content)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('view_post', post_id=post_id))

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    comment = conn.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()

    # Optional: only allow comment owner to delete
    if comment and comment['user_id'] == session['user_id']:
        conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
    
    conn.close()

    return redirect(url_for('view_post', post_id=comment['post_id']))

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        conn.close()
        flash("User not found.")
        return redirect(url_for('index'))

    # Count followers and following
    follower_count = conn.execute(
        'SELECT COUNT(*) FROM followers WHERE following_id = ?', (user_id,)
    ).fetchone()[0]
    following_count = conn.execute(
        'SELECT COUNT(*) FROM followers WHERE follower_id = ?', (user_id,)
    ).fetchone()[0]

    # Check if the logged-in user is following the profile user
    is_following = conn.execute(
        'SELECT 1 FROM followers WHERE follower_id = ? AND following_id = ?',
        (session['user_id'], user_id)
    ).fetchone() is not None

    # Fetch public posts of the user
    posts = conn.execute('''
        SELECT posts.*, users.username 
        FROM posts
        JOIN users ON posts.user_id = users.id
        WHERE posts.is_public = 1 AND users.id = ?
        ORDER BY posts.timestamp DESC
    ''', (user_id,)).fetchall()

    conn.close()

    return render_template('profile.html',
                           user=user,
                           follower_count=follower_count,
                           following_count=following_count,
                           is_following=is_following,
                           posts=posts)

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Check if the user has already liked the post
    existing_like = conn.execute('SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?',
                                 (session['user_id'], post_id)).fetchone()

    if existing_like is None:
        # Add like
        conn.execute('INSERT INTO likes (user_id, post_id) VALUES (?, ?)', 
                     (session['user_id'], post_id))
        conn.commit()

        # Increment like count
        conn.execute('UPDATE posts SET like_count = like_count + 1 WHERE id = ?', (post_id,))
        conn.commit()

    conn.close()
    return redirect(url_for('index'))

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()

    # Check if already following
    following = conn.execute('SELECT 1 FROM followers WHERE follower_id = ? AND following_id = ?',
                             (session['user_id'], user_id)).fetchone()

    if following is None:
        # Follow the user
        conn.execute('INSERT INTO followers (follower_id, following_id) VALUES (?, ?)', 
                     (session['user_id'], user_id))
    else:
        # Unfollow the user
        conn.execute('DELETE FROM followers WHERE follower_id = ? AND following_id = ?', 
                     (session['user_id'], user_id))

    conn.commit()
    conn.close()

    return redirect(url_for('profile', user_id=user_id))

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts WHERE is_public = 1 ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if 'profile_pic' not in request.files:
        flash("No file selected.")
        return redirect(url_for('profile', user_id=session['user_id']))

    file = request.files['profile_pic']

    if file.filename == '':
        flash("No file selected.")
        return redirect(url_for('profile', user_id=session['user_id']))

    filename = secure_filename(file.filename)
    
    # Generate a unique filename using user_id and current timestamp
    unique_filename = f"{session['user_id']}_{int(time.time())}_{filename}"
    
    filepath = os.path.join('static/uploads', unique_filename)
    file.save(filepath)

    # Update the database with the new file path
    conn = get_db_connection()
    conn.execute('UPDATE users SET profile_pic = ? WHERE id = ?', (filepath, session['user_id']))
    conn.commit()
    conn.close()

    flash("Profile picture updated.")
    return redirect(url_for('profile', user_id=session['user_id']))

@app.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    conn = get_db_connection()

    # Fetch post details
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    if not post:
        conn.close()
        flash("Post not found.")
        return redirect(url_for('index'))

    # Fetch comments for this post
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()

    conn.close()

    return render_template('view_post.html', post=post, comments=comments)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
