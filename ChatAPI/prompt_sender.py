import httpx
import json

class Sender:

    def __init__(self, 
                 params,
                 index,flag):
        
        self.params = params
        self.index = index
        try:
          self.flag = int(flag)
        except ValueError:
          self.flag = 0  
        self.sender_initializer()

    def sender_initializer(self):

        with open(self.params, "r") as json_file:
            params = json.load(json_file)

        self.channelid=params['channelid']
        self.authorization=params['authorization']
        self.application_id = params['application_id']
        self.guild_id = params['guild_id']
        self.session_id = params['session_id']
        self.version = params['version']
        self.id = params['id']
        self.flags = params['flags']
        self.timeout = 10
        
        
    def send(self, prompt):
        header = {
            'authorization': self.authorization,
            'sec-fetch-dest': 'empty',
            'origin': 'https://discord.com',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'zh-CN',
            'x-discord-timezone': 'Asia/Shanghai',
            'referer': 'https://discord.com/channels/943543313368223754/943543313368223760',
            # 'Connection': 'close'
        }
        payload = {'type': 2,
        'application_id': self.application_id,
        'guild_id': self.guild_id,
        'channel_id': self.channelid[self.index],
        'session_id': self.session_id,
        'data': {
            'version': self.version,
            'id': self.id,
            'name': 'imagine',
            'type': 1,
            'options': [{'type': 3, 'name': 'prompt', 'value': str(prompt) + ' ' + self.flags[self.flag]}],
            'attachments': [],
                }
            }
        response = httpx.post('https://discord.com/api/v9/interactions', headers=header, json=payload)

        print(response.status_code)

        while response.status_code != 204:

            response = httpx.post('https://discord.com/api/v9/interactions', json=payload, headers=header)

        # print(r.text)

        print('prompt [{}] successfully sent!'.format(prompt))
