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
