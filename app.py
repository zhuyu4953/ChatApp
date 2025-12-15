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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: # 如果已登录，重定向到首页
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password or not confirm_password:
            flash('所有字段都是必填项！', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('两次输入的密码不一致！', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已被注册，请选择其他用户名！', 'error')
            return render_template('register.html')

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，注册成功！请登录。', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # 如果已登录，重定向到首页
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('无效的用户名或密码！', 'error')
            return render_template('login.html')
        login_user(user, remember=False) # 登录用户
        flash('登录成功！', 'success')
        # 登录成功后，更新用户的最后在线时间
        user.last_seen = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('login.html')

# 注销路由
@app.route('/logout')
@login_required # 只有登录用户才能注销
def logout():
    logout_user()
    flash('您已成功注销。', 'info')
    return redirect(url_for('login'))


# --- SocketIO 事件处理 ---
@socketio.on('connect')
def test_connect():
    print(f'Client {current_user.username if current_user.is_authenticated else "anonymous"} connected.')
    #emit('my_response', {'data': 'Connected!'}, broadcast=True) # 广播连接信息

@socketio.on('disconnect')
def test_disconnect():
    print(f'Client {current_user.username if current_user.is_authenticated else "anonymous"} disconnected.')
    #emit('my_response', {'data': 'Disconnected!'}, broadcast=True) # 广播断开信息


with app.app_context():
    db.create_all() 

if __name__ == '__main__':
    print("Database tables created or already exist.")
    socketio.run(app, debug=True, port=5000)