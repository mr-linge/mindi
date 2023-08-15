import uuid
from functools import wraps

import httpx,json,os
from flask import Flask, jsonify, request, make_response
from flask_gzip import Gzip
from shopifyApis.mystore import shopify_utils
from utils.tools import Split_Picture, compress_image, uuid_filter,get_task
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)

import os

def create_static_directory():
    directory = "static"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"{directory} 目录已创建。")
    else:
        print(f"{directory} 目录已存在。")

import nltk
nltk.download('punkt')  # 下载必要的数据文件

consumption_time = {}

from gevent import monkey
monkey.patch_all()

from flask_cors import CORS
from datetime import datetime, timedelta
# from chatgpt import *
from processing_data import (
    get_user, insert_token, get_token_info, update_token, day_diff, get_config
)
from prompt_sender import Sender
from url_receiver import Receiver
from upsender import Sender as UpSender
import threading,time,re,sqlite3
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
app = Flask(__name__)
CORS(app, origins="*")  # 允许所有跨域访问，但可能存在安全风险
gzip = Gzip(app)
# 初始化 Profiler
# CORS(app, origins="https://example.com")  # 添加 origins 参数以限制允许的来源
global timeout_error_message
timeout_error_message = None
app.config['JWT_SECRET_KEY'] = get_config()['jwt_secret_key']  # JWT_SECRET_KEY 随机只有自己知道就行，可在 ../envs/configs 里修改
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)  # Token有效期为30天
jwt = JWTManager(app)

current_directory = os.path.dirname(os.path.abspath(__file__))
params = os.path.join(current_directory, 'sender_params.json')
with open(params, 'r') as f:
    sender_params = json.load(f)
channelid = sender_params['channelid']

# 设置单日用户最大请求次数
Request_Count = 10

with open('./file/Types.json','r',encoding='utf-8') as f:
    productType_list = json.loads(f.read())['productType']
# 是否通过 是否申请

four_list = []



def is_valid_uuid(uuid_str):
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return str(uuid_obj) == uuid_str
    except ValueError:
        return False

def measure_execution_time(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        code_lines = f.__code__.co_code.split(b"\n")
        line_count = len(code_lines)

        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()

        elapsed_time = end_time - start_time

        line_times = [elapsed_time / line_count] * line_count
        total_time = sum(line_times)

        percentages = [round(time / total_time * 100, 2) for time in line_times]

        for i, line in enumerate(code_lines):
            print(f"代码行 {i + 1} 执行时间：{line_times[i]:.4f} 秒，百分比：{percentages[i]:.2f}%")

        return result

    return wrapper

def validate_bank_card(card_number):
    # 移除卡号中的非数字字符
    card_number = ''.join(c for c in card_number if c.isdigit())

    # 将卡号逆序并将每个奇数位数字乘以2
    digits = [int(c) for c in card_number[::-1]]
    doubled_digits = [2 * digit if i % 2 == 1 else digit for i, digit in enumerate(digits)]

    # 将乘以2后的数字中的两位数拆分为个位数
    summed_digits = [digit // 10 + digit % 10 for digit in doubled_digits]

    # 计算所有数字的总和
    total = sum(summed_digits)

    # 验证卡号是否有效
    if total % 10 == 0:
        return True
    else:
        return False

def init_db():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    ## 个人画廊历史记录
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (message_id TEXT PRIMARY KEY, url TEXT, filename TEXT,email TEXT,productId TEXT,is_apply INTEGER default 0,images_num INTEGER,parent_image TEXT,productType TEXT,thread_index INTEGER)''')
    conn.commit()
    conn.close()

def reset_request_in_progress(available_thread_index):
    global request_in_progress
    global timeout_error_message

    with request_in_progress_lock:
        request_in_progress[available_thread_index] = False
    timeout_error_message = 'request timeout !'

def extract_uuid(filename):
  uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
  match = re.search(uuid_pattern, filename)
  if match:
    return match.group(0)
  else:
    return None


def get_message_id_from_db(filename, db_path):
  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # 查询数据库以获取与 filename 相关联的 message_id
  cursor.execute("SELECT message_id,productType FROM images WHERE filename=?",
                 (filename,))
  result = cursor.fetchone()

  if result:
    message_id = result
  else:
    message_id = None

  conn.close()
  return message_id


def get_thread_index_from_db(filename, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT thread_index FROM images WHERE filename=?", (filename, ))
    result = cursor.fetchone()

    if result:
        thread_index = result[0]
    else:
        thread_index = None

    conn.close()
    return thread_index

def clear_database(db_path):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("DELETE FROM images")
  conn.commit()
  conn.close()

# 24小时刷新数据库
def clear_database_every_24_hours(db_path):
  while True:
    time.sleep(24 * 60 * 60)  # 等待24小时（24小时 * 60分钟 * 60秒）
    # clear_database(db_path)


def download_image(url):

  response = httpx.get(url)
  filename = secure_filename(os.path.basename(urlparse(url).path))
  image_path = os.path.join('static', filename)

  with open(image_path, 'wb') as f:
    f.write(response.content)

  return filename

# 修饰器函数，用于监控每行代码的运行时间和百分比


def print_stored_data():
  conn = sqlite3.connect('images.db')
  c = conn.cursor()
  c.execute("SELECT * FROM images")
  rows = c.fetchall()
  conn.close()

  print("Stored data in the database:")
  print("message_id | url | filename | email | productId | is_apply | images_num | parent_image | productType |thread_index")
  print("---------------------------------------------")
  for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | {row[8]} | {row[9]}")


# API接口路由
@app.route('/api/recognize', methods=['POST'])
# @measure_execution_time
def api():
    # 获取当前Token对应user
    # user = get_jwt_identity()

    user_send  = request.json if request.method == "POST" else request.args
    username = user_send.get('username')
    question = user_send.get('question')
    productType = user_send.get('productType')
    task_uuid = user_send.get('uuid')

    consumption_time[str(task_uuid)] = 10
    if user_send == None or all([username,question,productType])==False or productType not in productType_list or task_uuid == False:
        return jsonify(
            {'statu': False, 'message': 'Please enter the correct description!'}), 200


    # 查询用户是否存在，

    # 检查 token 对应 user 是否存在
    # token_info = get_token_info(user)
    # if not token_info:
    #     return jsonify({'statu': False, 'message': 'Token does not exist. Please contact the administrator to apply.'}), 401
    # 获取用户访问次数

    # count = token_info[2]
    # # @jwt_required() 只有token有效期内才能访问，所以无需再次判断
    # # 检查 Token 是否过期
    # if datetime.now() > token_info[3] :
    #     # 过期的 Token 状态设置为过期
    #     update_token(username=token_info[0], count=count, last_use_time=token_info[4])
    #     return jsonify({'statu': False, 'message': 'Token expired'}), 401
    # 检查访问次数是否需要重置（每日需要重置下次数）
    # 上次请求日期与当前日期相差大于等于一天，且count > 0
    # if day_diff(datetime.now().date(), token_info[4]) and count > 0:
        # 重置访问次数
        # count = 0
    # 检查Token访问次数是否达到限制
    # if count >= Request_Count:
    #     return jsonify({'statu': False, 'message': 'Token access limit reached.'}), 429
    # print("Please write a description for me, for example, "+str(user_send.get("q"))+".For use by mjdjourney")

    # try:
    #     messages = [
    #         {"role": "system", "content": "mindi"},
    #         {"role": "user", "content": "Please write a product description for me, for example, "+str(user_send.get("q"))+".For use by Midjourney"}
    #     ]
    #     print(messages)
    #     rsp = ask_gpt(messages=messages)
    # except Exception as e:
    #     return jsonify({'statu': False, 'message': f'An error occurred in the chatgpt request, {e}'}), 500

    global request_in_progress
    global timeout_error_message
    available_thread_index = None
    for i, in_progress in enumerate(request_in_progress):
        if not in_progress:
            available_thread_index = i
            break
    if available_thread_index is None:
        request_in_progress[len(request_in_progress) - 1] = False
        return jsonify({
            "statu": False,
            'message': 'The current queue is full, please try again late'
        })
    request_in_progress[available_thread_index] = True

    # try:
        # from pygtrans import Translate
        # from mtranslate import translate
        # text = translate(question, 'en')
    text = question
    # print(text.translatedText)
    # assert  == 'お知らせ下さい'
    # 使用Spacy进行分词
    # tokens = nltk.word_tokenize(text)
    # print(tokens)

    consumption_time[str(task_uuid)] = 30

    # mycheck = False
    # for j in tokens:
    #     for t in productType_list:
    #         if t.lower().replace("s",'') == j.lower().replace("s",'') and j.lower().replace("s",'') == productType.lower().replace("s",''):
    #             mycheck = True
    #
    # if mycheck == False:
    #     return jsonify({
    #         "statu": False,
    #         'message': 'Category corresponding error or no such category. Please re-enter or re-choose.'
    #     })

    # 从请求中获取关键词参数
    flag = request.args.get('flag', 0)
    custom_content = ", Please add a prompt that the generated images need to be produced by the factory as much as possible, not just imagined"
    prompt = str(text)
    sender = Sender(params, available_thread_index, flag)
    print("发送成功！")
    sender.send(prompt)

    # 使用 Receiver 类接收图片 URL
    receiver = Receiver(params, available_thread_index)
    receiver.collecting_results()

    initial_image_timestamp = receiver.latest_image_timestamp

    consumption_time[str(task_uuid)] = 55

    # 设置最大等待时间
    max_wait_time = 300  # 最大等待时间，单位为秒

    # 创建一个定时器，在最大等待时间后重置request_in_progress标志
    timeout_timer = threading.Timer(max_wait_time, reset_request_in_progress, args=(available_thread_index,))
    timeout_timer.start()

    # 等待新图片出现
    wait_time = 0
    while wait_time < max_wait_time:

        receiver.collecting_results()
        current_image_timestamp = receiver.latest_image_timestamp

        if current_image_timestamp and current_image_timestamp > initial_image_timestamp:
            # 发现新图片，跳出循环
            timeout_timer.cancel()  # 取消定时器
            break

        # 等待一段时间
        time.sleep(1)
        wait_time += 1
        if consumption_time[str(task_uuid)]<90:
            consumption_time[str(task_uuid)] = consumption_time[str(task_uuid)]+1


    if current_image_timestamp and current_image_timestamp > initial_image_timestamp:
        latest_image_id = receiver.df.index[-1]
        latest_image_url = receiver.df.loc[latest_image_id].url
        latest_filename = receiver.df.loc[latest_image_id].filename

        # cdn = user_send.get('cdn', False)
        # print(cdn)
        # if cdn == True:

        image_filename = download_image(latest_image_url)
        latest_image_url = f"/static/{image_filename}"

        conn = sqlite3.connect('images.db')
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO images (message_id, url, filename,email,productType,thread_index) VALUES (?, ?, ?, ?, ?, ?)",
            (latest_image_id, latest_image_url, latest_filename,username,productType,available_thread_index))
        conn.commit()
        conn.close()

        # 图片分割
        # Split_Picture(image_filename)

        # 输出存储在数据库中的数据
        print_stored_data()

    else:
        latest_image_url = None
    with request_in_progress_lock:
        request_in_progress[available_thread_index] = False
    # 将最新图片的URL作为响应返回
    if timeout_error_message:
        response = jsonify({"statu": False,'message': timeout_error_message})
        timeout_error_message = None
        return response

    consumption_time[str(task_uuid)] = 100
    # 模拟压缩过程，每秒增加进度百分比
    # for i in range(1, 11):
    #     time.sleep(1)
    #     progress = i * 10
    #     # 将进度发送给前端
    #     return jsonify({'progress': progress})
    consumption_time.pop(str(task_uuid))

    return jsonify({'latest_image_url': latest_image_url,"statu": True,'message':"Successfully generated !"})
    # except Exception as e:
    #     print(f"Error: {e}")
    #     with request_in_progress_lock:
    #         request_in_progress[available_thread_index] = False
    #     return jsonify({'message': str(e),"statu": False})




    # 增加Token访问次数
    # count+= 1
    # last_use_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # update_token(username=token_info[0], count=count, last_use_time=last_use_time)
    # 返回API响应
    # return jsonify({'statu': True, 'message': rsp}), 200

## 保存产品的图片
@app.route('/api/upscale', methods=['POST'])
def upscale():

    global request_in_progress
    global timeout_error_message
    user_send = request.json if request.method == "POST" else request.args
    file_name = user_send.get('file_name')
    number = user_send.get('number')
    username = user_send.get('username')

    if file_name is None or number is None or username is None:
        return jsonify({'statu': False,'message': 'Parameter error Please try again！'})

    thread_index = get_thread_index_from_db(file_name, 'images.db')

    if thread_index is None:
        return jsonify({'statu': False,'message': f'No thread_index found for file_name: {file_name}'})

    if request_in_progress[thread_index]:

        return jsonify({
            'statu': False,
            'message': 'The current queue is full, please try again later'})

    request_in_progress[thread_index] = True

    message_id = get_message_id_from_db(file_name, 'images.db')

    if message_id is None:
        return jsonify(
        {'statu': False,'message': f'No message_id found for file_name: {file_name}'})

    ## 更新操作
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    myresult = c.execute(
        """select url from images WHERE email=? and images_num=? and parent_image=?""",
        (username,number,file_name)).fetchone()
    conn.close()
    if myresult!=None:
        return jsonify(
            {'statu': False, 'message': 'Submitted or not approved!'}), 200

    try:
        sender = UpSender(params, thread_index)
        uuid = extract_uuid(file_name)

        sender.send(message_id[0], number, uuid)

        # 使用 Receiver 类接收图片 URL
        receiver = Receiver(params, thread_index)
        receiver.collecting_results()

        initial_image_timestamp = receiver.latest_image_timestamp

        # 等待新图片出现
        max_wait_time = 10  # 最大等待时间，单位为秒
        wait_time = 0
        while wait_time < max_wait_time:
            receiver.collecting_results()
            current_image_timestamp = receiver.latest_image_timestamp
            print(current_image_timestamp)
            print(initial_image_timestamp)
            if current_image_timestamp and (current_image_timestamp > initial_image_timestamp):
            # 发现新图片，跳出循环
                break
        # 等待一段时间
            time.sleep(1)
            wait_time += 1
        if current_image_timestamp and (current_image_timestamp > initial_image_timestamp):
            latest_image_id = receiver.df.index[-1]
            latest_image_url = receiver.df.loc[latest_image_id].url
            latest_filename = receiver.df.loc[latest_image_id].filename

            # cdn =  user_send.get('cdn', False)
            # if cdn == True:

            image_filename = download_image(latest_image_url)
            latest_image_url = f"/static/{image_filename}"

            conn = sqlite3.connect('images.db')
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO images (message_id, url, filename,email,images_num,parent_image,productType,thread_index) VALUES (?, ?, ?, ?, ?, ? , ?, ?)",
                (latest_image_id, latest_image_url, latest_filename,username,number,file_name,message_id[1],thread_index))
            conn.commit()
            conn.close()
            print_stored_data()
            # compress_image("." + latest_image_url, "." + latest_image_url, 100)

        else:
            latest_image_url = None

        with request_in_progress_lock:
            request_in_progress[thread_index] = False

        if latest_image_url == None:
            return jsonify({'statu': False,'latest_image_url': latest_image_url, "message": "Do not duplicate！"})
        else:

            ## 图片增加到shopify后台
            shopify_utils.add_product(username, message_id[1], '.'+latest_image_url)
            return jsonify(
                {'statu': True, 'message': 'The application is successful!'}), 200


    except Exception as e:
        print(f"Error: {e}")
        with request_in_progress_lock:
            request_in_progress[thread_index] = False
        return jsonify({'statu': False,'message': str(e)})

@app.route('/api/addUserCard', methods=['POST'])
def addUserCard():
    user_send  = request.json if request.method == "POST" else request.args
    username = user_send.get('username')
    idcard = user_send.get('idcard')
    if all([username,idcard])==False:
        return jsonify({'statu': False,'message': 'Parameter error Please try again！'})
    if validate_bank_card(idcard) == False:
        return jsonify({'statu': False, 'message': 'Card number error ！'})
    result = shopify_utils.update_idcard(username, idcard)
    return jsonify(result)

@app.route('/api/product', methods=['POST'])
def mproduct():
    user_send = request.json if request.method == "POST" else request.args
    send_type = user_send.get('send_type')
    if send_type == 0:
        username = user_send.get('username')
        if username == None:
            return jsonify({'statu': False, 'message': 'User name error ！'})
        return jsonify({'statu': True, 'message': 'success ！','data':shopify_utils.get_all_products(username,send_type)})
    elif send_type == 1:
        return jsonify({'statu': True, 'message': 'success ！','data':shopify_utils.get_all_products(None, send_type)})
    else:
        return jsonify({'statu': False, 'message': 'fail ！'})


# @app.route('/static/<string:post_slug>')
@app.route('/static/<string:post_slug>')
def get_image(post_slug):
    # 读取图片文件
    image_path = './static/'+post_slug
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # 创建响应对象
    response = make_response(image_data)

    # 设置响应头
    response.headers['Content-Type'] = 'image/png'
    response.headers['Content-Length'] = len(image_data)

    # 设置缓存策略
    expires = datetime.now() + timedelta(days=30)
    response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response

@app.route('/api/monitoring/status',methods=["GET"])
def uuid_view():
    uuid_str1 = request.args.get("task_uuid")
    if uuid_str1 == None or is_valid_uuid(uuid_str1) == False:
        return jsonify({'statu': False, 'message': 'fail ！'})
    return jsonify({'statu': True, 'message': 'success ！',"schedule":consumption_time.get(str(uuid_str1))})

# @app.route('/test', methods=['GET'])
# def mytest():
#     # 模拟压缩过程，每秒增加进度百分比
#     for i in range(1, 11):
#         time.sleep(1)
#         progress = i * 10
#         # 将进度发送给前端
#         return jsonify({'progress': progress})
#     return jsonify({'success': True})


# Token生成路由
@app.route('/token', methods=['POST'])
def token():
    # 获取用户名和密码
    username = request.json.get('u', None)
    password = request.json.get('p', None)
    user = get_user(username)
    # 检查用户名和密码是否正确
    if not user or password != user[2]:
        return jsonify({'statu': False, 'message': 'Invalid username or password'}), 200
    try:
        # 每个用户只能有一个token
        token_info = get_token_info(username)
        if token_info:
            return jsonify({'statu': True, 'message': {'username': username, 'token': token_info[1], 'expiration_time': token_info[3]}}), 200
        # 生成Token
        token = create_access_token(identity=username)
        # 记录到数据表
        expiration_time = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        insert_token(username, token, expiration_time)
    except Exception as e:
        return jsonify({'statu': False, 'message': f'Error in create token, Exception: {e}'}), 500
    # 返回Token
    return jsonify({'statu': True, 'message': {'username': username, 'token': token, 'expiration_time': expiration_time}}), 201

def refresh_token(db):
    while True:
        time.sleep(24 * 60 * 60)  # 等待24小时（24小时 * 60分钟 * 60秒）
        for i, in_progress in enumerate(request_in_progress):
            if in_progress == True:
                request_in_progress[i] = False

if __name__ == '__main__':

    num_threads = len(channelid)
    request_in_progress = [False] * num_threads
    # print(request_in_progress)
    request_in_progress_lock = threading.Lock()

    init_db()
    db_path = 'images.db'
    clear_db_thread = threading.Thread(target=refresh_token,
                                       args=(db_path,))
    clear_db_thread.daemon = True  # 设置为守护线程，这样在主程序结束时，线程也会结束
    clear_db_thread.start()

    print_stored_data()
    # ssl证书加密
    # sslify = SSLify(app, ssl_context=(
    #     "server/server-cert.crt",
    #     "server/server-key.key"))

    # app.config['SSL_CONTEXT'] = ("server/server-cert.crt", "server/server-key.key")

    # from gevent import pywsgi
    # import ssl
    # context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2
    # context.load_cert_chain('server/server-cert.crt','server/server-key.key')
    # app.debug = True
    # server = pywsgi.WSGIServer(('0.0.0.0', 443), app, ssl_context=context)
    # server.serve_forever()

    # app.run(host="0.0.0.0", port=443)
    app.run(host="127.0.0.1", port=77,ssl_context=(
        "server/server-cert.crt",
        "server/server-key.key")
    )


