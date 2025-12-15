# ChatApp/app.py (更新后的版本)

from flask import Flask, render_template, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from config import Config
from models import db, User, Message 
from datetime import datetime 

app = Flask(__name__)
app.config.from_object(Config) 

db.init_app(app) 
socketio = SocketIO(app, cors_allowed_origins='*')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required 
def index():
    return render_template('chat.html') 


with app.app_context():
    db.create_all() 

if __name__ == '__main__':
    print("Database tables created or already exist.")
    socketio.run(app, debug=True, port=5000)