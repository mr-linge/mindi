# from flask_socketio import SocketIO, emit
# from flask import Flask, render_template
# from time import sleep
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret'
# socketio = SocketIO(app)
#
#
# @socketio.on('progress')
# def handle_progress(data):
#     total_progress = 100
#     for i in range(total_progress + 1):
#         sleep(0.1)  # 模拟耗时操作
#         emit('progress_update', {'progress': i}, broadcast=True)
#     emit('progress_complete', {'message': 'Progress complete!'}, broadcast=True)
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# if __name__ == '__main__':
#     socketio.run(app,port=)