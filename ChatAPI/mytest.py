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

import requests

# cookies = {
#     '__dcfduid': 'ebc9edf0247f11ee9aa2696675b403a8',
#     '__sdcfduid': 'ebc9edf1247f11ee9aa2696675b403a86e0c01a36db47a19ca0bed6e2fa20476c531fcb91f6e4a5c3fc611007338f913',
#     'cf_clearance': 'hBzVfVrI0CVcG1SR2GLcOhDMC_TVMWRUELj6y5K837Y-1691984093-0-1-15419117.9c43357e.4240cef7-0.2.1691984093',
#     'locale': 'zh-CN',
#     '__cfruid': '4e04bd348afda4f262ef131a6c085f790f2aaf6d-1692071906',
# }

headers = {
    # 'authority': 'discord.com',
    # 'accept': '*/*',
    # 'accept-language': 'en-US,en;q=0.5',
    'authorization': 'OTIxMzAzMjA1OTE5NDkwMDY4.GMngzo.lzL5Y_r12iUcgCPu6BA7jFjnMAMpI_YVO93xuI',
    # 'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary6s46BzJdk038AZOt',
    # Requests sorts cookies= alphabetically
    # 'cookie': '__dcfduid=ebc9edf0247f11ee9aa2696675b403a8; __sdcfduid=ebc9edf1247f11ee9aa2696675b403a86e0c01a36db47a19ca0bed6e2fa20476c531fcb91f6e4a5c3fc611007338f913; cf_clearance=hBzVfVrI0CVcG1SR2GLcOhDMC_TVMWRUELj6y5K837Y-1691984093-0-1-15419117.9c43357e.4240cef7-0.2.1691984093; locale=zh-CN; __cfruid=4e04bd348afda4f262ef131a6c085f790f2aaf6d-1692071906',
    'origin': 'https://discord.com',
    'referer': 'https://discord.com/channels/943543313368223754/943543313368223760',
    # 'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'x-debug-options': 'bugReporterEnabled',
    'x-discord-locale': 'zh-CN',
    'x-discord-timezone': 'Asia/Shanghai',
    # 'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEwOS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTA5LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3d3dy5taWRqb3VybmV5LmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluIjoid3d3Lm1pZGpvdXJuZXkuY29tIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjIxOTgzOSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=',
}

# data = {"type":2,"application_id":"936929561302675456","guild_id":"943543313368223754","channel_id":"943543313368223760","session_id":"9375ef36fc6186a9cc82fbfd2c6ac604","data":{"version":"1118961510123847772","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"rings"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1118961510123847772","default_member_permissions":None,"type":1,"nsfw":False,"name":"imagine","description":"Create images with Midjourney","dm_permission":True,"contexts":[0,1,2],"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":True}]},"attachments":[]},"nonce":"1140862509545160704"}
data = {'type': 2, 'application_id': '936929561302675456', 'guild_id': '943543313368223754', 'channel_id': '1130403150570979369', 'session_id': '24bf0be628127cfa22c82b41d5b56521', 'data': {'version': '1118961510123847772', 'id': '938956540159881230', 'name': 'imagine', 'type': 1, 'options': [{'type': 3, 'name': 'prompt', 'value': 'rings --v 5'}], 'attachments': []}}
response = requests.post('https://discord.com/api/v9/interactions',headers=headers, json=data,verify=False)

print(response.status_code)

# data = '------WebKitFormBoundary6s46BzJdk038AZOt\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{"type":2,"application_id":"936929561302675456","guild_id":"943543313368223754","channel_id":"943543313368223760","session_id":"9375ef36fc6186a9cc82fbfd2c6ac604","data":{"version":"1118961510123847772","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"rings"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1118961510123847772","default_member_permissions":null,"type":1,"nsfw":false,"name":"imagine","description":"Create images with Midjourney","dm_permission":true,"contexts":[0,1,2],"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":true}]},"attachments":[]},"nonce":"1140862509545160704"}\r\n------WebKitFormBoundary6s46BzJdk038AZOt--\r\n'

# response = requests.post('https://discord.com/api/v9/interactions', cookies=cookies, headers=headers, json=data,verify=False)
#
# print(response.status_code)


