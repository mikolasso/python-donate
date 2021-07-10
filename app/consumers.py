import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import time

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'chat',
            self.channel_name
        )
        self.accept()
    # def disconnect(self, close_code):
    #     pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        # text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # self.send(text_data=json.dumps({
        #     'message': message
        # }))
        self.send(text_data=message)
        async_to_sync(self.channel_layer.group_send)(
            'chat',
            {
                'type': 'chat_message',
                'message': text_data
            }
        )
        
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
        
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            'chat',
            self.channel_name
        )