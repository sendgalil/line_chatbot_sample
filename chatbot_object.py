# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 19:26:23 2018

@author: Galil
"""


import json
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

class chatbot(object):
    def __init__(self, client_id, client_secret, question_data_path, 
                 response_data_path):
        with open(question_data_path) as f:
            question_data = json.load(f)
        with open(response_data_path) as f:
            response_data = json.load(f)
        short_token = self.get_short_token(client_id, client_secret)
        self.line_bot_api = LineBotApi(short_token)
        self.template_data = self.create_template(question_data)
        self.response_data = self.create_response(response_data)
        self.user_list = {}
    #Methods
    def get_short_token(self, client_id, client_secret):
        #獲得短期的token (30天)
        post_data = {'grant_type': 'client_credentials', 
                'client_id': client_id, 
                'client_secret': client_secret}
        post_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post('https://api.line.me/v2/oauth/accessToken', 
                          data = post_data, headers = post_headers)
        temp_json = json.loads(r.text)
        token = temp_json['access_token']
        return token
    def create_template(self, question_data):
        #依據不同的框架類型產生對應框架
        template_data = {} 
        for thing in question_data:
            if (thing['template_type'] == 'ImageCarousel_template'):
                temp_columns = []                
                for column in thing['columns']:
                    temp = ImageCarouselColumn(
                                image_url=column['image_url'],
                                action=PostbackAction(
                                    label=column['label'],
                                    data=column['data']
                                )
                            )
                    temp_columns.append(temp)
                template_message = TemplateSendMessage(
                    alt_text='ImageCarousel template',
                    template=ImageCarouselTemplate(
                        columns=temp_columns
                    )
                )
                template_data[thing['key_word']] = template_message
            elif (thing['template_type'] == 'Text_message'):
                template_data[thing['key_word']] = TextSendMessage(text=thing['text'])
        return template_data
    def create_response(self, temp_response_data):
        response_data = {}
        for thing in temp_response_data:
            if (thing['type'] == 'text'):
                response_message = TextSendMessage(text=thing['text'])
                response_data[thing['key_word']] = response_message
        return response_data
    def create_task_template(self, uid, task):
        task_template = {'task':'',
                         'report_message':''}
        #依據自定義的任務創建回覆的框架訊息
        if task == '建議與問題回報':            
            task_template['task'] = 'suggestion'
            self.user_list[uid] = task_template
            response_text = ('感謝您的使用，請直接輸入您的問題或是建議，想離開的話'
                            '請按結束回報即可')
            response_template = TemplateSendMessage(
                                alt_text='Carousel template',
                                template=CarouselTemplate(
                                    columns=[
                                        CarouselColumn(
                                            title='建議與問題回報',
                                            text=response_text,
                                            actions=[
                                                PostbackAction(
                                                    label='結束回報',
                                                    data='message_type=end_of_return'
                                               )
                                            ]
                                        )
                                    ]
                                )
                            )
        elif task == 'search':
            task_template['task'] = 'search'
            self.user_list[uid] = task_template
            response_text = '請直接輸入關鍵字即可搜尋'
            response_template = TextSendMessage(text=response_text)
        
        return response_template