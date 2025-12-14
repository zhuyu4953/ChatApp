from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key_wan_zi_jie_2025'

socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return '<h1>Hello World! ChatApp is running by Wan Zijie.</h1>'

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)